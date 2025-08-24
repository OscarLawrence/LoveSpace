from pydantic import BaseModel
from typing import Dict, Any

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    token_usage: Dict[str, Any] = {}