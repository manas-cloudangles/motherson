from fastapi import APIRouter, HTTPException
from app.schemas.audit import AuditRequest, AuditResponse
from app.services.audit_service import AuditService

router = APIRouter()

@router.post("/audit", response_model=AuditResponse)
async def audit_code(request: AuditRequest):
    try:
        # Prepare the input dict
        code_input = {
            "html": request.html,
            "ts": request.ts,
            "css": request.css
        }
        
        # Call the service
        final_code = await AuditService.orchestrate_agents(code_input, request.user_request)
        
        # Since orchestrate_agents returns just the code (best_code), 
        # we wrap it in our response format.
        # Note: If you want the "audit_summary" passed back, 
        # you might need to adjust orchestrate_agents to return it too.
        # For now, we return the refined code.
        
        return AuditResponse(
            status="completed",
            refined_code=final_code,
            audit_summary={} # Placeholder as service currently returns only code
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))