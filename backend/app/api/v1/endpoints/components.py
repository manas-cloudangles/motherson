from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import List, Dict, Any
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
from app.services.workspace_service import WorkspaceService

router = APIRouter()

# Dependency injection for services could be added here, 
# but for now we'll instantiate them directly or use singletons if needed.
# Since they are stateless or file-based, instantiation is fine.
metadata_service = MetadataService()
workspace_service = WorkspaceService()

@router.post("/upload-and-analyze", response_model=Dict[str, Any])
async def upload_and_analyze(
    files: List[UploadFile] = File(...),
    pageRequest: str = Form(...)
):
    temp_dir = None
    try:
        if not pageRequest or not pageRequest.strip():
            raise HTTPException(status_code=400, detail="Page request is required")
        
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")

        # Save page request
        workspace_service.save_page_request(pageRequest)
        
        # Create temp dir
        temp_dir = Path(tempfile.mkdtemp(prefix="angular_components_"))
        
        for file in files:
            relative_path = file.filename
            if not relative_path:
                continue
            
            file_path = temp_dir / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            content = await file.read()
            file_path.write_bytes(content)
            
        # Analyze
        metadata = await metadata_service.analyze_components_from_files(temp_dir)
        
        if not metadata:
             raise HTTPException(status_code=500, detail="Failed to generate metadata")

        # Save metadata
        metadata_service.save_metadata(metadata)
        
        return {
            "status": "success",
            "components": metadata,
            "message": f"Analyzed {len(metadata)} components successfully"
        }

    except Exception as e:
        print(f"Error in upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_dir and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

@router.post("/select-components", response_model=ComponentSelectResponse)
async def select_components(request_data: ComponentSelectRequest):
    try:
        page_request = request_data.pageRequest or workspace_service.load_page_request()
        if not page_request:
            raise HTTPException(status_code=400, detail="Page request is required")
            
        metadata = metadata_service.load_metadata()
        if not metadata:
             raise HTTPException(status_code=400, detail="No metadata available")
             
        selection = await metadata_service.select_components(page_request, metadata)
        
        updated_metadata = metadata_service.update_metadata_with_selection(selection, metadata)
        metadata_service.save_metadata(updated_metadata)
        
        selected_components = [c for c in updated_metadata if c.get('required')]
        
        return {
            "status": "success",
            "all_components": updated_metadata,
            "selected_component_ids": selection.get('selected_components', []),
            "reasoning": selection.get('reasoning', {}),
            "selected_components": selected_components
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
