"""
Session management endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Message
from app.api.models.schemas import SessionCreate, SessionResponse, SessionDetail
from app.core.agent_service import ComputerUseAgentService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new agent session"""
    try:
        agent_service = ComputerUseAgentService(db)
        session = await agent_service.create_session(session_data.name)
        
        return SessionResponse(
            id=session.id,
            name=session.name,
            status=session.status,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[SessionResponse])
async def get_sessions(db: Session = Depends(get_db)):
    """Get all sessions"""
    try:
        agent_service = ComputerUseAgentService(db)
        sessions = agent_service.get_all_sessions()
        
        result = []
        for session in sessions:
            # Count messages for each session
            message_count = db.query(Message).filter(Message.session_id == session.id).count()
            
            result.append(SessionResponse(
                id=session.id,
                name=session.name,
                status=session.status,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=message_count
            ))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=SessionDetail)
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get session details with messages"""
    try:
        agent_service = ComputerUseAgentService(db)
        session = agent_service.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get session messages
        messages = db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.timestamp).all()
        
        return SessionDetail(
            id=session.id,
            name=session.name,
            status=session.status,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=len(messages),
            messages=[
                {
                    "id": msg.id,
                    "session_id": msg.session_id,
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "message_metadata": msg.message_metadata,  # Changed from metadata
                    "tool_executions": []  # TODO: Include tool executions
                }
                for msg in messages
            ]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a session"""
    try:
        agent_service = ComputerUseAgentService(db)
        success = agent_service.delete_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": f"Session {session_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 