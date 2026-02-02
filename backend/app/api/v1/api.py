from fastapi import APIRouter
from app.api.v1.endpoints import components, generation, chat, system, audit, tasks, integration

api_router = APIRouter()

api_router.include_router(system.router, prefix="", tags=["System"])
api_router.include_router(components.router, prefix="", tags=["Components"]) # Orig API didn't have prefix for select/update
api_router.include_router(generation.router, prefix="", tags=["Generation"])
api_router.include_router(chat.router, prefix="", tags=["Chat"])
api_router.include_router(audit.router, prefix="", tags=["Audit"])
api_router.include_router(tasks.router, prefix="", tags=["Tasks"])
api_router.include_router(integration.router, prefix="/integration", tags=["Integration"])

