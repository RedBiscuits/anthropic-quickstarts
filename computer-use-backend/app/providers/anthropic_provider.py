"""
Anthropic AI provider implementation with proper error handling and fallback
"""
import logging
import os
from typing import List, Dict, Any, Optional
from anthropic import AsyncAnthropic
from anthropic.types import Message as AnthropicMessage

from app.core.interfaces import AIProvider
from app.core.validation import ValidationService
from app.core.exceptions import ProviderError, ValidationError

logger = logging.getLogger(__name__)


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider implementation"""
    
    def __init__(self, validation_service: ValidationService):
        self.validation_service = validation_service
        self.client = self._initialize_client()
        self.model_name = os.getenv('MODEL_NAME', 'claude-sonnet-4-20250514')
    
    def _initialize_client(self) -> Optional[AsyncAnthropic]:
        """Initialize Anthropic client with validation"""
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                logger.warning("ANTHROPIC_API_KEY not set")
                return None
            
            # Validate API key
            validation_result = self.validation_service.validate_api_key(api_key)
            if not validation_result.is_valid:
                logger.error(f"Invalid API key format: {validation_result.error_message}")
                return None
            
            client = AsyncAnthropic(api_key=api_key)
            logger.info(f"Anthropic client initialized with model: {self.model_name}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            return None
    
    async def generate_response(
        self, 
        user_message: str, 
        conversation_history: List[Dict[str, Any]],
        progress_callback: Optional[callable] = None
    ) -> str:
        """Generate AI response using Anthropic Claude"""
        try:
            if not self.client:
                raise ProviderError("Anthropic client not initialized")
            
            # Validate input
            if not user_message or not isinstance(user_message, str):
                raise ValidationError("User message is required and must be a string")
            
            if progress_callback:
                await progress_callback("thinking", "Processing your request with Claude...")
            
            # Prepare messages for Claude
            messages = self._prepare_messages(user_message, conversation_history)
            
            # Call Claude API
            if progress_callback:
                await progress_callback("thinking", "Generating response...")
            
            response = await self.client.messages.create(
                model=self.model_name,
                messages=messages,
                max_tokens=4000,
                temperature=0.7
            )
            
            if progress_callback:
                await progress_callback("completed", "Response generated successfully")
            
            # Extract and return response content
            response_content = response.content[0].text if response.content else ""
            
            logger.info(f"Generated response with {len(response_content)} characters")
            return response_content
            
        except Exception as e:
            logger.error(f"Error generating response with Anthropic: {e}")
            raise ProviderError(f"Failed to generate response: {str(e)}")
    
    def _prepare_messages(
        self, 
        user_message: str, 
        conversation_history: List[Dict[str, Any]]
    ) -> List[AnthropicMessage]:
        """Prepare messages for Claude API"""
        messages = []
        
        # Add conversation history
        for msg in conversation_history[-10:]:  # Limit to last 10 messages
            role = "user" if msg.get("role") == "user" else "assistant"
            content = msg.get("content", "")
            if content:
                messages.append(AnthropicMessage(role=role, content=content))
        
        # Add current user message
        messages.append(AnthropicMessage(role="user", content=user_message))
        
        return messages
    
    def is_available(self) -> bool:
        """Check if provider is available"""
        return self.client is not None


class FallbackProvider(AIProvider):
    """Fallback provider for when Anthropic is not available"""
    
    async def generate_response(
        self, 
        user_message: str, 
        conversation_history: List[Dict[str, Any]],
        progress_callback: Optional[callable] = None
    ) -> str:
        """Generate fallback response"""
        try:
            if progress_callback:
                await progress_callback("thinking", "Using fallback response system...")
            
            # Simple fallback logic
            if "weather" in user_message.lower():
                response = "I would search for weather information, but I'm currently in fallback mode. Please check your API key configuration."
            elif "search" in user_message.lower():
                response = "I would perform a web search, but I'm currently in fallback mode. Please check your API key configuration."
            else:
                response = "I understand your request, but I'm currently in fallback mode. Please check your Anthropic API key configuration to enable full functionality."
            
            if progress_callback:
                await progress_callback("completed", "Fallback response generated")
            
            logger.info("Generated fallback response")
            return response
            
        except Exception as e:
            logger.error(f"Error generating fallback response: {e}")
            return "I'm sorry, but I'm unable to process your request at the moment. Please try again later." 