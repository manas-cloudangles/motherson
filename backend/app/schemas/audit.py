from pydantic import BaseModel
from typing import Optional

class AuditRequest(BaseModel):
    html: str
    ts: str
    css: Optional[str] = ""

class AuditResponse(BaseModel):
    status: str
    refined_code: dict
    audit_summary: Optional[dict] = None