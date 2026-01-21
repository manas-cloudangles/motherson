from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.generation_service import GenerationService
from app.services.workspace_service import WorkspaceService

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
             
        new_html = new_data.get('html_code', html)
        new_scss = new_data.get('scss_code', scss)
        new_ts = new_data.get('ts_code', ts)
        
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
