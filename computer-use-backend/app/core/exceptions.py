"""
Custom exceptions for the application
"""


class BaseError(Exception):
    """Base exception class for the application"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(BaseError):
    """Exception raised for validation errors"""
    def __init__(self, message: str, field_name: str = None):
        self.field_name = field_name
        super().__init__(message, "VALIDATION_ERROR")


class RepositoryError(BaseError):
    """Exception raised for repository/database errors"""
    def __init__(self, message: str):
        super().__init__(message, "REPOSITORY_ERROR")


class ServiceError(BaseError):
    """Exception raised for service layer errors"""
    def __init__(self, message: str):
        super().__init__(message, "SERVICE_ERROR")


class ProviderError(BaseError):
    """Exception raised for external provider errors"""
    def __init__(self, message: str):
        super().__init__(message, "PROVIDER_ERROR")


class WebSocketError(BaseError):
    """Exception raised for WebSocket errors"""
    def __init__(self, message: str):
        super().__init__(message, "WEBSOCKET_ERROR")


class ConfigurationError(BaseError):
    """Exception raised for configuration errors"""
    def __init__(self, message: str):
        super().__init__(message, "CONFIGURATION_ERROR") 