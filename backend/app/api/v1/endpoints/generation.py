import asyncio
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.schemas.page import GeneratePageRequest, GeneratePageResponse
from app.services.generation_service import GenerationService
from app.services.metadata_service import MetadataService
from app.services.workspace_service import WorkspaceService
from app.services.audit_service import AuditService
from app.services.task_store import TaskStore, TaskStatus

router = APIRouter()

generation_service = GenerationService()
metadata_service = MetadataService()
workspace_service = WorkspaceService()
task_store = TaskStore()

async def process_generation_task(task_id: str, page_request: str, required_components: list):
    try:
        # 1. Generate Draft
        page_data = await generation_service.generate_page(page_request, required_components)
        
        if not page_data:
            task_store.update_task_error(task_id, "Failed to generate page")
            return

        # 2. Prepare for Audit
        code_input = {
            "html": page_data['html_code'],
            "css": page_data['scss_code'],
            "ts": page_data['ts_code'],
            "component_name": page_data['component_name'],
            "path_name": page_data['path_name'],
            "selector": page_data['selector']
        }

        # 3. Perform Audit (SSB)
        final_code = await AuditService.orchestrate_agents(code_input, page_request)

        # 4. Update data with audited code
        page_data['html_code'] = final_code.get('html', page_data['html_code'])
        page_data['scss_code'] = final_code.get('css', page_data['scss_code'])
        page_data['ts_code'] = final_code.get('ts', page_data['ts_code'])
             
        # 5. Save State
        workspace_service.save_state(
            page_data['html_code'],
            page_data['scss_code'],
            page_data['ts_code'],
            page_request
        )
        
        # 6. Prepare Final Result
        result = {
            "status": "success",
            "html_code": page_data['html_code'],
            "scss_code": page_data['scss_code'],
            "ts_code": page_data['ts_code'],
            "component_name": page_data['component_name'],
            "path_name": page_data['path_name'],
            "selector": page_data['selector']
        }
        
        # 7. Mark Complete
        task_store.update_task_result(task_id, result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        task_store.update_task_error(task_id, str(e))

@router.post("/generate-page", response_model=Dict[str, Any])
async def generate_page(request_data: GeneratePageRequest):
    try:
        # 1. Validation & Setup
        page_request = request_data.pageRequest or workspace_service.load_page_request()
        if not page_request:
             raise HTTPException(status_code=400, detail="Page request is required")
             
        all_metadata = metadata_service.load_metadata()
        if not all_metadata:
             raise HTTPException(status_code=400, detail="No metadata available")
             
        required_components = []
        for comp in all_metadata:
             req = comp.get('required', False)
             is_req = False
             if isinstance(req, bool):
                 is_req = req
             elif isinstance(req, str):
                 is_req = req.lower() == 'true'
             
             if is_req:
                 required_components.append(comp)

        # 2. Create Task
        task_id = task_store.create_task()
        
        # 3. Start Background Process
        asyncio.create_task(process_generation_task(task_id, page_request, required_components))
        
        # 4. Return Task ID
        return {
            "status": "processing",
            "task_id": task_id
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))