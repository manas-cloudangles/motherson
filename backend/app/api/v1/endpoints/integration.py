from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from app.services.integration_service import IntegrationService

router = APIRouter()
integration_service = IntegrationService()

class IntegrateRequest(BaseModel):
    component_name: str

@router.post("/generate-snippets")
async def generate_snippets(request: IntegrateRequest):
    try:
        if not request.component_name:
             raise HTTPException(status_code=400, detail="Component name is required")
             
        snippets = integration_service.generate_snippets(request.component_name)
        
        return {
            "status": "success",
            "snippets": snippets
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
