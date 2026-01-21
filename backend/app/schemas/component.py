from typing import List, Dict, Optional
from pydantic import BaseModel

class ComponentSelectRequest(BaseModel):
    pageRequest: str

class ComponentSelectResponse(BaseModel):
    status: str
    all_components: List[Dict]
    selected_component_ids: List[str]
    reasoning: Dict[str, str]
    selected_components: List[Dict]

class UpdateComponentMetadataRequest(BaseModel):
    components: List[Dict]  # List of components with updated required and reasoning fields

class UpdateComponentMetadataResponse(BaseModel):
    status: str
    message: str
