"""
Core interfaces and abstractions following SOLID principles
"""
from abc import ABC, abstractmethod
from typing import Protocol, Dict, Any, Optional, List
from datetime import datetime

from app.database.models import Session, Message, ToolExecution
from app.api.models.schemas import SessionCreate, MessageCreate


class SessionRepository(Protocol):
    """Repository interface for session operations"""
    
    def create(self, session_data: SessionCreate) -> Session:
        """Create a new session"""
        ...
    
    def get_by_id(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        ...
    
    def get_all(self) -> List[Session]:
        """Get all sessions"""
        ...
    
    def update(self, session_id: str, **kwargs) -> Optional[Session]:
        """Update session"""
        ...
    
    def delete(self, session_id: str) -> bool:
        """Delete session"""
        ...


class MessageRepository(Protocol):
    """Repository interface for message operations"""
    
    def create(self, message_data: MessageCreate) -> Message:
        """Create a new message"""
        ...
    
    def get_by_session(self, session_id: str) -> List[Message]:
        """Get messages by session ID"""
        ...
    
    def get_by_id(self, message_id: str) -> Optional[Message]:
        """Get message by ID"""
        ...


class AIProvider(Protocol):
    """AI provider interface for different LLM services"""
    
    async def generate_response(
        self, 
        user_message: str, 
        conversation_history: List[Dict[str, Any]],
        progress_callback: Optional[callable] = None
    ) -> str:
        """Generate AI response"""
        ...


class WebSocketManager(Protocol):
    """WebSocket manager interface"""
    
    async def connect(self, websocket, session_id: str) -> None:
        """Connect WebSocket to session"""
        ...
    
    async def disconnect(self, websocket, session_id: str) -> None:
        """Disconnect WebSocket from session"""
        ...
    
    async def broadcast_to_session(
        self, 
        session_id: str, 
        message_type: str, 
        data: Dict[str, Any]
    ) -> None:
        """Broadcast message to session"""
        ...


class ValidationService(Protocol):
    """Validation service interface"""
    
    def validate_session_name(self, name: str) -> bool:
        """Validate session name"""
        ...
    
    def validate_message_content(self, content: str) -> bool:
        """Validate message content"""
        ...
    
    def validate_session_id(self, session_id: str) -> bool:
        """Validate session ID format"""
        ...


class EventPublisher(Protocol):
    """Event publisher interface for domain events"""
    
    async def publish_session_created(self, session: Session) -> None:
        """Publish session created event"""
        ...
    
    async def publish_message_sent(self, message: Message) -> None:
        """Publish message sent event"""
        ...
    
    async def publish_agent_response(self, message: Message) -> None:
        """Publish agent response event"""
        ... 