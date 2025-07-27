"""
WebSocket Connection Manager for real-time streaming
"""
import json
import logging
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect

from app.api.models.schemas import WebSocketMessage

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time communication"""
    
    def __init__(self):
        # Store active connections by session_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        
        self.active_connections[session_id].append(websocket)
        logger.info(f"WebSocket connected for session {session_id}. Total connections: {len(self.active_connections[session_id])}")
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove a WebSocket connection"""
        if session_id in self.active_connections:
            try:
                self.active_connections[session_id].remove(websocket)
                logger.info(f"WebSocket disconnected for session {session_id}")
                
                # Clean up empty session lists
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]
            except ValueError:
                logger.warning(f"Attempted to remove non-existent connection for session {session_id}")
    
    async def send_message(self, session_id: str, message: WebSocketMessage):
        """Send a message to all connections for a session"""
        if session_id not in self.active_connections:
            logger.warning(f"No active connections for session {session_id}")
            return
        
        # Convert message to JSON
        message_json = message.model_dump_json()
        
        # Send to all connections for this session
        disconnected_connections = []
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending message to WebSocket: {e}")
                disconnected_connections.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected_connections:
            self.disconnect(connection, session_id)
    
    async def broadcast_to_session(self, session_id: str, message_type: str, data: dict):
        """Broadcast a message to all connections in a session"""
        message = WebSocketMessage(type=message_type, data=data)
        await self.send_message(session_id, message)
    
    def get_connection_count(self, session_id: str) -> int:
        """Get the number of active connections for a session"""
        return len(self.active_connections.get(session_id, []))
    
    def get_all_sessions(self) -> List[str]:
        """Get all session IDs with active connections"""
        return list(self.active_connections.keys())


# Global WebSocket manager instance
websocket_manager = WebSocketManager() 