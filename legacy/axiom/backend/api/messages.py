"""
Message handling API endpoints
RESTful interface for message operations
"""
from typing import List

from core.contracts import contract_enforced
from core.session_manager import Message, SessionManager
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/messages", tags=["messages"])

# Dependency to get session manager
def get_session_manager() -> SessionManager:
    import main
    return main.session_manager


class MessageRequest(BaseModel):
    """Request model for sending messages"""
    content: str


class MessageResponse(BaseModel):
    """Response model for messages"""
    role: str
    content: str
    tool_calls: List[str]
    timestamp: str


@router.get("/{session_id}", response_model=List[MessageResponse])
@contract_enforced(
    postconditions=["returns list of messages for session"],
    description="Get all messages for session"
)
async def get_messages(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
) -> List[MessageResponse]:
    """Get all messages for a session"""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return [
        MessageResponse(
            role=msg.role,
            content=msg.content,
            tool_calls=msg.tool_calls,
            timestamp=msg.timestamp.isoformat()
        )
        for msg in session.messages
    ]