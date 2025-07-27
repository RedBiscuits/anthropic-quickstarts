"""
Pydantic models for API request/response validation
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.database.models import SessionStatus, MessageRole, ToolExecutionStatus


# Session schemas
class SessionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Session name")


class SessionResponse(BaseModel):
    id: str
    name: str
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True


class SessionDetail(SessionResponse):
    messages: List["MessageResponse"] = []


# Message schemas
class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, description="Message content")


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: MessageRole
    content: str
    timestamp: datetime
    message_metadata: Dict[str, Any] = {}  # Changed from 'metadata' to 'message_metadata'
    tool_executions: List["ToolExecutionResponse"] = []

    class Config:
        from_attributes = True


# Tool execution schemas
class ToolExecutionResponse(BaseModel):
    id: str
    message_id: str
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    status: ToolExecutionStatus
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# WebSocket message schemas
class WebSocketMessage(BaseModel):
    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(default_factory=dict, description="Message data")


class AgentProgressMessage(WebSocketMessage):
    type: str = "agent_progress"
    message: str
    step: Optional[str] = None
    progress: Optional[float] = None


class ToolExecutionMessage(WebSocketMessage):
    type: str = "tool_execution"
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: Optional[Dict[str, Any]] = None
    status: ToolExecutionStatus


class AgentResponseMessage(WebSocketMessage):
    type: str = "agent_response"
    content: str
    message_id: str


# Update forward references
SessionDetail.model_rebuild()
MessageResponse.model_rebuild()
ToolExecutionResponse.model_rebuild() 