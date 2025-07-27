"""
Message management endpoints
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Message
from app.api.models.schemas import MessageCreate, MessageResponse
from app.core.agent_service import ComputerUseAgentService
from app.core.websocket_manager import websocket_manager

router = APIRouter(prefix="/sessions", tags=["messages"])


@router.post("/{session_id}/messages", response_model=MessageResponse)
async def send_message(
    session_id: str,
    message_data: MessageCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Send a message to an agent session"""
    try:
        agent_service = ComputerUseAgentService(db)
        
        # Verify session exists
        session = agent_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Create WebSocket callback for real-time streaming
        async def websocket_callback(message):
            await websocket_manager.send_message(session_id, message)
        
        # Process message in background to avoid blocking
        async def process_message_task():
            try:
                await agent_service.process_message(
                    session_id=session_id,
                    user_message=message_data.content,
                    websocket_callback=websocket_callback
                )
            except Exception as e:
                # Send error to WebSocket
                await websocket_manager.broadcast_to_session(
                    session_id,
                    "error",
                    {"message": str(e)}
                )
        
        # Start background task
        background_tasks.add_task(process_message_task)
        
        # Return immediate response - actual processing happens in background
        return MessageResponse(
            id="processing",
            session_id=session_id,
            role="user",
            content=message_data.content,
            timestamp=datetime.utcnow(),
            message_metadata={"status": "processing"},
            tool_executions=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(session_id: str, db: Session = Depends(get_db)):
    """Get all messages for a session"""
    try:
        agent_service = ComputerUseAgentService(db)
        
        # Verify session exists
        session = agent_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get messages
        messages = db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.timestamp).all()
        
        return [
            MessageResponse(
                id=msg.id,
                session_id=msg.session_id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp,
                message_metadata=msg.message_metadata,
                tool_executions=[]  # TODO: Include tool executions
            )
            for msg in messages
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 