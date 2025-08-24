"""
Session management API endpoints
RESTful interface for session operations
"""
from typing import Any, Dict, List

from core.contracts import contract_enforced
from core.session_manager import CollaborationStage, Session, SessionManager
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/sessions", tags=["sessions"])

# Dependency to get session manager
def get_session_manager() -> SessionManager:
    # Import main module from the application
    import main
    return main.session_manager


class SessionResponse(BaseModel):
    """Response model for session data"""
    id: str
    stage: str
    message_count: int
    active_task_count: int
    project_context: Dict[str, Any]
    created_at: str


class StageChangeRequest(BaseModel):
    """Request model for changing collaboration stage"""
    stage: str


@router.post("/", response_model=SessionResponse)
async def create_session(
    session_manager: SessionManager = Depends(get_session_manager)
) -> SessionResponse:
    """Create a new collaboration session"""
    session = session_manager.create_session()
    
    return SessionResponse(
        id=session.id,
        stage=session.stage.value,
        message_count=len(session.messages),
        active_task_count=len(session.active_tasks),
        project_context=session.project_context,
        created_at=session.created_at.isoformat()
    )


@router.get("/{session_id}", response_model=SessionResponse)
@contract_enforced(
    preconditions=["session_id is valid UUID"],
    description="Get session by ID"
)
async def get_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
) -> SessionResponse:
    """Get session by ID"""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionResponse(
        id=session.id,
        stage=session.stage.value,
        message_count=len(session.messages),
        active_task_count=len(session.active_tasks),
        project_context=session.project_context,
        created_at=session.created_at.isoformat()
    )


@router.post("/{session_id}/stage")
@contract_enforced(
    description="Change collaboration stage for session"
)
async def change_stage(
    session_id: str,
    request: StageChangeRequest,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Change collaboration stage for session"""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        new_stage = CollaborationStage(request.stage)
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid stage: {request.stage}"
        )
    
    await session_manager.change_stage(session_id, new_stage)
    
    return {"status": "success", "new_stage": new_stage.value}


@router.get("/{session_id}/tasks")
@contract_enforced(
    description="Get task tree for session"
)
async def get_tasks(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Get task tree for session"""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    tasks = []
    for task in session.active_tasks:
        tasks.append({
            "id": task.id,
            "description": task.description,
            "status": task.status.value,
            "progress": task.progress,
            "subtasks": [
                {
                    "id": subtask.id,
                    "description": subtask.description,
                    "status": subtask.status.value,
                    "progress": subtask.progress
                }
                for subtask in task.subtasks
            ]
        })
    
    return {"tasks": tasks}