from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.generation_service import GenerationService
from app.services.workspace_service import WorkspaceService

from app.services.audit_service import AuditService

router = APIRouter()

generation_service = GenerationService()
workspace_service = WorkspaceService()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_page(request_data: ChatRequest):
    try:
        user_message = request_data.message
        if not user_message:
             raise HTTPException(status_code=400, detail="Message is required")
             
        session = workspace_service.load_state()
        if not session or 'current_state' not in session:
             raise HTTPException(status_code=400, detail="No active session found")
             
        state = session['current_state']
        html = state.get('html', '')
        scss = state.get('scss', '')
        ts = state.get('ts', '')
        
        new_data = await generation_service.chat_with_page(html, scss, ts, user_message)
        
        if not new_data:
             raise HTTPException(status_code=500, detail="Failed to get chat response")
            
        code_input = {
            "html": new_data['html_code'],
            "css": new_data['scss_code'],
            "ts": new_data['ts_code'],
        }

        final_code = await AuditService.orchestrate_agents(code_input, user_message)
             
        new_html = final_code.get('html', new_data['html_code'])
        new_scss = final_code.get('css', new_data['scss_code'])
        new_ts = final_code.get('ts', new_data['ts_code'])
        
        workspace_service.save_state(new_html, new_scss, new_ts, user_message)
        
        return {
            "status": "success",
            "html_code": new_html,
            "scss_code": new_scss,
            "ts_code": new_ts,
            "message": "Successfully updated code"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
