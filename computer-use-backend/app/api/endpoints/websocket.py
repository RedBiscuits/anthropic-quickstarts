"""
WebSocket endpoint for real-time communication
"""
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.agent_service import ComputerUseAgentService
from app.core.websocket_manager import websocket_manager

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time session updates"""
    try:
        # Accept connection
        await websocket_manager.connect(websocket, session_id)
        
        # Send initial connection message
        await websocket_manager.broadcast_to_session(
            session_id,
            "connection",
            {"message": "Connected to session", "session_id": session_id}
        )
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (optional)
                data = await websocket.receive_text()
                logger.info(f"Received WebSocket message for session {session_id}: {data}")
                
                # Echo back or handle client messages if needed
                await websocket_manager.broadcast_to_session(
                    session_id,
                    "client_message",
                    {"message": data}
                )
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for session {session_id}")
                break
            except Exception as e:
                logger.error(f"Error in WebSocket connection for session {session_id}: {e}")
                break
                
    except Exception as e:
        logger.error(f"Error establishing WebSocket connection for session {session_id}: {e}")
    finally:
        # Clean up connection
        websocket_manager.disconnect(websocket, session_id) 