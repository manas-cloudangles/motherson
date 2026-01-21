from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    status: str
    html_code: str
    scss_code: str
    ts_code: str
    message: str
