from fastapi import APIRouter
from app.schemas.common import HealthResponse, ResetResponse
from app.services.workspace_service import WorkspaceService
from app.services.metadata_service import MetadataService

router = APIRouter()
workspace_service = WorkspaceService()
metadata_service = MetadataService()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return {"status": "ok", "message": "API is running"}

@router.post("/reset", response_model=ResetResponse)
async def reset_session():
    workspace_service.clear_state()
    # Also clear metadata file? Orig code did.
    if metadata_service.metadata_file.exists():
         metadata_service.metadata_file.unlink()
         
    return {"status": "success", "message": "Session reset"}
