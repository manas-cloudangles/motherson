from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.services.task_store import TaskStore

router = APIRouter()
task_store = TaskStore()

@router.get("/tasks/{task_id}", response_model=Dict[str, Any])
async def get_task_status(task_id: str):
    task = task_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task