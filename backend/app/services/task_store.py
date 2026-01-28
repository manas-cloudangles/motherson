import uuid
from typing import Dict, Any, Optional
from enum import Enum

# Define possible states for a task
class TaskStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskStore:
    # Singleton instance - ensures we only have ONE store across the app
    _instance = None
    # The actual storage: a dictionary mapping task_id -> task_data
    _tasks: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskStore, cls).__new__(cls)
        return cls._instance

    # 1. Start a new task
    def create_task(self) -> str:
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = {
            "status": TaskStatus.PROCESSING,
            "result": None,
            "error": None
        }
        return task_id

    # 2. Mark task as success
    def update_task_result(self, task_id: str, result: Any):
        if task_id in self._tasks:
            self._tasks[task_id]["status"] = TaskStatus.COMPLETED
            self._tasks[task_id]["result"] = result

    # 3. Mark task as failed
    def update_task_error(self, task_id: str, error: str):
        if task_id in self._tasks:
            self._tasks[task_id]["status"] = TaskStatus.FAILED
            self._tasks[task_id]["error"] = error

    # 4. Read task status
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self._tasks.get(task_id)