from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.schemas.page import GeneratePageRequest, GeneratePageResponse

from app.services.generation_service import GenerationService
from app.services.metadata_service import MetadataService
from app.services.workspace_service import WorkspaceService

from app.services.audit_service import AuditService

router = APIRouter()

generation_service = GenerationService()
metadata_service = MetadataService()
workspace_service = WorkspaceService()

@router.post("/generate-page", response_model=GeneratePageResponse)
async def generate_page(request_data: GeneratePageRequest):
    try:
        page_request = request_data.pageRequest or workspace_service.load_page_request()
        if not page_request:
             raise HTTPException(status_code=400, detail="Page request is required")
             
        all_metadata = metadata_service.load_metadata()
        if not all_metadata:
             raise HTTPException(status_code=400, detail="No metadata available")
             
        # Filter for required components
        # Logic: required=True (boolean) or "true" (string)
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
        
        # if not required_components:
        #      raise HTTPException(status_code=400, detail="No required components selected")
             
        page_data = await generation_service.generate_page(page_request, required_components)
        
        if not page_data:
             raise HTTPException(status_code=500, detail="Failed to generate page")

        code_input = {
            "html": page_data['html_code'],
            "css": page_data['scss_code'],
            "ts": page_data['ts_code'],
            "component_name": page_data['component_name'],
            "path_name": page_data['path_name'],
            "selector": page_data['selector']
        }

        final_code = await AuditService.orchestrate_agents(code_input)

        page_data['html_code'] = final_code.get('html', page_data['html_code'])
        page_data['scss_code'] = final_code.get('css', page_data['scss_code'])
        page_data['ts_code'] = final_code.get('ts', page_data['ts_code'])
             
        workspace_service.save_state(
            page_data['html_code'],
            page_data['scss_code'],
            page_data['ts_code'],
            page_request
        )
        
        return {
            "status": "success",
            "html_code": page_data['html_code'],
            "scss_code": page_data['scss_code'],
            "ts_code": page_data['ts_code'],
            "component_name": page_data['component_name'],
            "path_name": page_data['path_name'],
            "selector": page_data['selector']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
