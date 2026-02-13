import asyncio
from app.services.task_store import TaskStore, TaskStatus
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import List, Dict, Any, Optional
import shutil
import tempfile
from pathlib import Path

from app.schemas.component import (
    ComponentSelectRequest,
    ComponentSelectResponse,
    UpdateComponentMetadataRequest,
    UpdateComponentMetadataResponse
)
from app.services.metadata_service import MetadataService
from app.services.backend_api_service import BackendApiService
from app.services.workspace_service import WorkspaceService

task_store = TaskStore()
router = APIRouter()

# Dependency injection for services could be added here, 
# but for now we'll instantiate them directly or use singletons if needed.
# Since they are stateless or file-based, instantiation is fine.
metadata_service = MetadataService()
backend_api_service = BackendApiService()
workspace_service = WorkspaceService()

@router.post("/upload-and-analyze", response_model=Dict[str, Any])
async def upload_and_analyze(
    frontendFiles: Optional[List[UploadFile]] = File(default=[]),
    backendFiles: Optional[List[UploadFile]] = File(default=[]),
    pageRequest: str = Form(...)
):
    """
    Upload and analyze both frontend (Angular) and backend (PHP) files.
    
    Parameters:
    - frontendFiles: List of Angular component files (.ts, .html, .scss)
    - backendFiles: List of PHP backend API files (.php)
    - pageRequest: Description of the page to generate
    
    Returns metadata for both frontend components and backend APIs.
    """
    frontend_temp_dir = None
    backend_temp_dir = None
    
    try:
        if not pageRequest or not pageRequest.strip():
            raise HTTPException(status_code=400, detail="Page request is required")
        
        if not frontendFiles and not backendFiles:
            raise HTTPException(status_code=400, detail="No files uploaded. Please upload frontend and/or backend files.")

        print(f"Received {len(frontendFiles or [])} frontend files and {len(backendFiles or [])} backend files for analysis")
        
        # Save page request
        workspace_service.save_page_request(pageRequest)
        
        # === ANALYZE FRONTEND FILES ===
        frontend_metadata = []
        if frontendFiles and len(frontendFiles) > 0:
            # Create temp dir for frontend
            frontend_temp_dir = Path(tempfile.mkdtemp(prefix="angular_components_"))
            print(f"Created frontend temp directory: {frontend_temp_dir}")
            
            for file in frontendFiles:
                relative_path = file.filename
                if not relative_path:
                    continue
                
                file_path = frontend_temp_dir / relative_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                content = await file.read()
                file_path.write_bytes(content)
                print(f"  Saved frontend: {relative_path}")
            
            # Analyze frontend components
            frontend_metadata = await metadata_service.analyze_components_from_files(frontend_temp_dir)
            print(f"Analyzed {len(frontend_metadata)} frontend components")
        
        # === ANALYZE BACKEND FILES ===
        backend_metadata = []
        if backendFiles and len(backendFiles) > 0:
            # Create temp dir for backend
            backend_temp_dir = Path(tempfile.mkdtemp(prefix="php_apis_"))
            print(f"Created backend temp directory: {backend_temp_dir}")
            
            for file in backendFiles:
                relative_path = file.filename
                if not relative_path:
                    continue
                
                file_path = backend_temp_dir / relative_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                content = await file.read()
                file_path.write_bytes(content)
                print(f"  Saved backend: {relative_path}")
            
            # Analyze backend APIs
            backend_metadata = await backend_api_service.analyze_apis_from_files(backend_temp_dir)
            print(f"Analyzed {len(backend_metadata)} backend APIs")
        
        # Save metadata
        if frontend_metadata:
            metadata_service.save_metadata(frontend_metadata)
        
        if backend_metadata:
            backend_api_service.save_metadata(backend_metadata)
        
        return {
            "status": "success",
            "frontend_components": frontend_metadata,
            "backend_apis": backend_metadata,
            "message": f"Analyzed {len(frontend_metadata)} frontend components and {len(backend_metadata)} backend APIs successfully"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp directories
        if frontend_temp_dir and frontend_temp_dir.exists():
            try:
                shutil.rmtree(frontend_temp_dir)
            except:
                pass
        
        if backend_temp_dir and backend_temp_dir.exists():
            try:
                shutil.rmtree(backend_temp_dir)
            except:
                pass

@router.post("/select-components", response_model=Dict[str, Any])
async def select_components(request_data: ComponentSelectRequest):
    try:
        page_request = request_data.pageRequest or workspace_service.load_page_request()
        if not page_request:
            raise HTTPException(status_code=400, detail="Page request is required")
        
        task_id = task_store.create_task()

        asyncio.create_task(process_selection_task(task_id, page_request))

        return {
            "status": "processing",
            "task_id": task_id
        }

    except Exception as e:
        print(f"Error in select_components: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_selection_task(task_id: str, page_request: str):
    try:
        # Load both frontend and backend metadata
        frontend_metadata = metadata_service.load_metadata()
        backend_metadata = backend_api_service.load_metadata()
        
        if not frontend_metadata and not backend_metadata:
            task_store.update_task_error(task_id, "No metadata available")
            return
        
        # Select frontend components
        frontend_selection = {}
        updated_frontend_metadata = []
        selected_frontend = []
        
        if frontend_metadata:
            frontend_selection = await metadata_service.select_components(page_request, frontend_metadata)
            updated_frontend_metadata = metadata_service.update_metadata_with_selection(frontend_selection, frontend_metadata)
            metadata_service.save_metadata(updated_frontend_metadata)
            selected_frontend = [c for c in updated_frontend_metadata if c.get('required')]
        
        # Select backend APIs
        backend_selection = {}
        updated_backend_metadata = []
        selected_backend = []
        
        if backend_metadata:
            backend_selection = await backend_api_service.select_apis(page_request, backend_metadata)
            updated_backend_metadata = backend_api_service.update_metadata_with_selection(backend_selection, backend_metadata)
            backend_api_service.save_metadata(updated_backend_metadata)
            selected_backend = [api for api in updated_backend_metadata if api.get('required')]
        
        result = {
            # Frontend components
            "all_components": updated_frontend_metadata,
            "selected_component_ids": frontend_selection.get('selected_components', []),
            "component_reasoning": frontend_selection.get('reasoning', {}),
            "selected_components": selected_frontend,
            
            # Backend APIs
            "all_apis": updated_backend_metadata,
            "selected_api_ids": backend_selection.get('selected_apis', []),
            "api_reasoning": backend_selection.get('reasoning', {}),
            "selected_apis": selected_backend
        }

        task_store.update_task_result(task_id, result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in process_selection_task: {e}")
        task_store.update_task_error(task_id, str(e))

            
@router.post("/update-component-metadata", response_model=UpdateComponentMetadataResponse)
async def update_component_metadata(request_data: UpdateComponentMetadataRequest):
    try:
        if not request_data.components:
             raise HTTPException(status_code=400, detail="Components list required")
             
        metadata_service.save_metadata(request_data.components)
        
        return {
            "status": "success",
            "message": f"Successfully updated metadata for {len(request_data.components)} components"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-api-metadata", response_model=Dict[str, Any])
async def update_api_metadata(request_data: Dict[str, Any]):
    """
    Update backend API metadata with user selections.
    
    Accepts a JSON object with:
    {
        "apis": [list of API objects with updated required and reasoning fields]
    }
    """
    try:
        apis = request_data.get('apis', [])
        if not apis:
             raise HTTPException(status_code=400, detail="APIs list required")
             
        backend_api_service.save_metadata(apis)
        
        return {
            "status": "success",
            "message": f"Successfully updated metadata for {len(apis)} backend APIs"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

