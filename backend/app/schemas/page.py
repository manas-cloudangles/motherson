from typing import List, Optional
from pydantic import BaseModel

class GeneratePageRequest(BaseModel):
    pageRequest: str
    selectedComponentIds: Optional[List[str]] = []

class GeneratePageResponse(BaseModel):
    status: str
    html_code: str
    scss_code: str
    ts_code: str
    component_name: str
    path_name: str
    selector: str
