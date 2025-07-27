"""
Validation service implementing business rules and data validation
"""
import re
from typing import Optional, Tuple
from dataclasses import dataclass

from app.core.exceptions import ValidationError


@dataclass
class ValidationResult:
    """Validation result with error details"""
    is_valid: bool
    error_message: Optional[str] = None
    field_name: Optional[str] = None


class ValidationService:
    """Service for validating business data and rules"""
    
    # Validation constants
    MIN_SESSION_NAME_LENGTH = 1
    MAX_SESSION_NAME_LENGTH = 255
    MIN_MESSAGE_LENGTH = 1
    MAX_MESSAGE_LENGTH = 10000
    UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
    
    def validate_session_name(self, name: str) -> ValidationResult:
        """Validate session name according to business rules"""
        if not name or not isinstance(name, str):
            return ValidationResult(
                is_valid=False,
                error_message="Session name is required and must be a string",
                field_name="name"
            )
        
        name = name.strip()
        
        if len(name) < self.MIN_SESSION_NAME_LENGTH:
            return ValidationResult(
                is_valid=False,
                error_message=f"Session name must be at least {self.MIN_SESSION_NAME_LENGTH} character long",
                field_name="name"
            )
        
        if len(name) > self.MAX_SESSION_NAME_LENGTH:
            return ValidationResult(
                is_valid=False,
                error_message=f"Session name cannot exceed {self.MAX_SESSION_NAME_LENGTH} characters",
                field_name="name"
            )
        
        # Check for potentially harmful content
        if self._contains_suspicious_content(name):
            return ValidationResult(
                is_valid=False,
                error_message="Session name contains potentially harmful content",
                field_name="name"
            )
        
        return ValidationResult(is_valid=True)
    
    def validate_message_content(self, content: str) -> ValidationResult:
        """Validate message content according to business rules"""
        if not content or not isinstance(content, str):
            return ValidationResult(
                is_valid=False,
                error_message="Message content is required and must be a string",
                field_name="content"
            )
        
        content = content.strip()
        
        if len(content) < self.MIN_MESSAGE_LENGTH:
            return ValidationResult(
                is_valid=False,
                error_message=f"Message content must be at least {self.MIN_MESSAGE_LENGTH} character long",
                field_name="content"
            )
        
        if len(content) > self.MAX_MESSAGE_LENGTH:
            return ValidationResult(
                is_valid=False,
                error_message=f"Message content cannot exceed {self.MAX_MESSAGE_LENGTH} characters",
                field_name="content"
            )
        
        # Check for potentially harmful content
        if self._contains_suspicious_content(content):
            return ValidationResult(
                is_valid=False,
                error_message="Message content contains potentially harmful content",
                field_name="content"
            )
        
        return ValidationResult(is_valid=True)
    
    def validate_session_id(self, session_id: str) -> ValidationResult:
        """Validate session ID format"""
        if not session_id or not isinstance(session_id, str):
            return ValidationResult(
                is_valid=False,
                error_message="Session ID is required and must be a string",
                field_name="session_id"
            )
        
        if not self.UUID_PATTERN.match(session_id):
            return ValidationResult(
                is_valid=False,
                error_message="Session ID must be a valid UUID format",
                field_name="session_id"
            )
        
        return ValidationResult(is_valid=True)
    
    def validate_api_key(self, api_key: str) -> ValidationResult:
        """Validate API key format"""
        if not api_key or not isinstance(api_key, str):
            return ValidationResult(
                is_valid=False,
                error_message="API key is required and must be a string",
                field_name="api_key"
            )
        
        if not api_key.startswith('sk-'):
            return ValidationResult(
                is_valid=False,
                error_message="API key must start with 'sk-'",
                field_name="api_key"
            )
        
        if len(api_key) < 20:
            return ValidationResult(
                is_valid=False,
                error_message="API key appears to be too short",
                field_name="api_key"
            )
        
        return ValidationResult(is_valid=True)
    
    def _contains_suspicious_content(self, text: str) -> bool:
        """Check for potentially harmful content"""
        suspicious_patterns = [
            r'<script.*?>',  # Script tags
            r'javascript:',  # JavaScript protocol
            r'data:text/html',  # Data URLs
            r'vbscript:',  # VBScript
            r'on\w+\s*=',  # Event handlers
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False