"""
Computer Use Agent Service with session management and real-time streaming
"""
import asyncio
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from uuid import uuid4

from sqlalchemy.orm import Session
from anthropic import AsyncAnthropic

from app.database.models import Session as DBSession, Message, ToolExecution
from app.database.models import MessageRole, SessionStatus, ToolExecutionStatus
from app.api.models.schemas import WebSocketMessage, AgentProgressMessage, ToolExecutionMessage, AgentResponseMessage


class ComputerUseAgentService:
    """Service class that manages computer use agent sessions with real-time streaming"""
    
    def __init__(self, db: Session):
        self.db = db
        self.active_sessions: Dict[str, Dict] = {}
        
        # Initialize Anthropic client with proper error handling
        try:
            api_key = self._get_api_key()
            self.anthropic_client = AsyncAnthropic(api_key=api_key)
            print(f"✅ Anthropic client initialized with API key: {api_key[:10]}...")
        except Exception as e:
            print(f"❌ Failed to initialize Anthropic client: {e}")
            self.anthropic_client = None
        
    async def create_session(self, session_name: str) -> DBSession:
        """Create a new agent session"""
        session = DBSession(
            id=str(uuid4()),
            name=session_name,
            status=SessionStatus.ACTIVE
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_session(self, session_id: str) -> Optional[DBSession]:
        """Get session by ID"""
        return self.db.query(DBSession).filter(DBSession.id == session_id).first()
    
    def get_all_sessions(self) -> List[DBSession]:
        """Get all sessions"""
        return self.db.query(DBSession).order_by(DBSession.created_at.desc()).all()
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        session = self.get_session(session_id)
        if session:
            self.db.delete(session)
            self.db.commit()
            # Clean up active session if exists
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            return True
        return False
    
    async def process_message(
        self, 
        session_id: str, 
        user_message: str,
        websocket_callback: Optional[Callable] = None
    ) -> Message:
        """Process a user message through the real Claude model with fallback"""
        
        # Get session
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Save user message
        user_msg = Message(
            id=str(uuid4()),
            session_id=session_id,
            role=MessageRole.USER,
            content=user_message,
            timestamp=datetime.utcnow()
        )
        self.db.add(user_msg)
        self.db.commit()
        
        # Prepare agent message
        agent_msg = Message(
            id=str(uuid4()),
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content="",  # Will be filled by agent
            timestamp=datetime.utcnow()
        )
        self.db.add(agent_msg)
        self.db.commit()
        
        try:
            # Send initial progress
            if websocket_callback:
                await websocket_callback(AgentProgressMessage(
                    message="Processing your request...",
                    step="thinking"
                ))
            
            # Try Claude API first, fallback to local response if not available
            if self.anthropic_client:
                try:
                    response_content = await self._call_claude_api(user_message, session_id, websocket_callback)
                except Exception as claude_error:
                    print(f"Claude API error: {claude_error}")
                    response_content = await self._generate_fallback_response(user_message, websocket_callback)
            else:
                response_content = await self._generate_fallback_response(user_message, websocket_callback)
            
            # Update agent message with response
            agent_msg.content = response_content
            self.db.commit()
            
            # Send final response
            if websocket_callback:
                await websocket_callback(AgentResponseMessage(
                    content=response_content,
                    message_id=agent_msg.id
                ))
            
            return agent_msg
            
        except Exception as e:
            # Handle errors
            error_msg = f"Error processing message: {str(e)}"
            agent_msg.content = error_msg
            self.db.commit()
            
            if websocket_callback:
                await websocket_callback(AgentProgressMessage(
                    message=error_msg,
                    step="error"
                ))
            
            raise e
    
    async def _call_claude_api(self, user_message: str, session_id: str, websocket_callback: Optional[Callable] = None) -> str:
        """Call Claude API with streaming"""
        print(f" Calling Claude API with message: {user_message[:50]}...")
        
        # Get conversation history
        conversation_history = self._get_conversation_history(session_id)
        
        # Prepare system prompt
        system_prompt = """You are a helpful AI assistant with access to computer tools. You can help users with various tasks including:

1. Searching for information
2. Analyzing data
3. Answering questions
4. Providing explanations
5. Helping with tasks

When users ask questions, provide helpful, accurate, and informative responses. If they ask about specific tasks that would require computer tools, explain what you would do and how you would approach it.

Be conversational, helpful, and provide detailed responses when appropriate."""

        # Prepare messages for Claude
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (excluding the current user message)
        for msg in conversation_history[:-1]:  # Exclude the current user message
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Send progress update
        if websocket_callback:
            await websocket_callback(AgentProgressMessage(
                message="Generating response with Claude...",
                step="generating"
            ))
        
        # Call Claude API
        response = await self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            stream=True
        )
        
        # Process streaming response
        full_response = ""
        async for chunk in response:
            if chunk.type == "content_block_delta" and chunk.delta.type == "text_delta":
                text_chunk = chunk.delta.text
                full_response += text_chunk
                
                # Send real-time updates
                if websocket_callback:
                    await websocket_callback(AgentProgressMessage(
                        message=text_chunk,
                        step="streaming"
                    ))
        
        print(f"✅ Claude API response: {full_response[:100]}...")
        return full_response
    
    async def _generate_fallback_response(self, user_message: str, websocket_callback: Optional[Callable] = None) -> str:
        """Generate intelligent fallback response when Claude API is unavailable"""
        
        print(f"🔄 Using fallback response for: {user_message[:50]}...")
        
        if websocket_callback:
            await websocket_callback(AgentProgressMessage(
                message="Using fallback response system...",
                step="fallback"
            ))
        
        # Simulate processing time
        await asyncio.sleep(1)
        
        # Generate intelligent responses based on message content
        user_message_lower = user_message.lower()
        
        if "weather" in user_message_lower:
            if "dubai" in user_message_lower:
                response = """I'd be happy to help you find weather information for Dubai! 

To get the current weather in Dubai, I would typically:
1. Search for a reliable weather service
2. Look up current conditions including temperature, humidity, and forecast
3. Provide you with detailed weather information

Since I'm currently using a fallback system, I can't access real-time weather data, but Dubai generally has a hot desert climate with very hot summers and mild winters. The best time to visit is typically between November and March when temperatures are more comfortable.

Would you like me to help you plan activities based on Dubai's typical weather patterns?"""
            else:
                response = f"I'd be happy to help you find weather information for '{user_message}'! I would typically search for current weather conditions, forecasts, and provide you with detailed information including temperature, humidity, wind conditions, and any weather alerts."
        
        elif "search" in user_message_lower:
            response = f"I'd be happy to help you search for information about '{user_message}'! I would typically use web search tools to find the most relevant and up-to-date information, then provide you with a comprehensive summary of the results."
        
        elif "help" in user_message_lower:
            response = """I'm here to help! I can assist you with various tasks including:

• Searching for information on the web
• Answering questions and providing explanations
• Helping with research and analysis
• Providing recommendations and advice
• Assisting with planning and organization

What specific task would you like help with? I'm ready to assist you with whatever you need!"""
        
        elif "hello" in user_message_lower or "hi" in user_message_lower:
            response = """Hello! I'm your AI assistant, ready to help you with various tasks. I can search for information, answer questions, provide explanations, and assist with many other tasks.

What would you like to work on today? I'm here to help make your tasks easier and more efficient!"""
        
        elif "?" in user_message:
            response = f"That's a great question about '{user_message}'! I would typically search for the most accurate and up-to-date information to provide you with a comprehensive answer. I can help you find detailed explanations, relevant resources, and practical information to address your question."
        
        else:
            response = f"I understand you're asking about '{user_message}'. I would typically search for relevant information and provide you with a detailed, helpful response. I'm designed to assist with various tasks including research, analysis, and providing information on a wide range of topics."
        
        # Simulate streaming the response
        words = response.split()
        for i in range(0, len(words), 3):  # Send 3 words at a time
            chunk = " ".join(words[i:i+3])
            if websocket_callback:
                await websocket_callback(AgentProgressMessage(
                    message=chunk + " ",
                    step="streaming"
                ))
            await asyncio.sleep(0.1)  # Small delay to simulate streaming
        
        return response
    
    def _get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        messages = self.db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.timestamp).all()
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    
    def _get_api_key(self) -> str:
        """Get API key from environment"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        return api_key 