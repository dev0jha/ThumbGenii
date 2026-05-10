"""
Custom Exceptions

Application-specific exception classes.
"""

from typing import Optional
from fastapi import HTTPException, status


class ThumbAIException(Exception):
    """Base application exception."""
    
    def __init__(self, message: str = "An error occurred", code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class AuthenticationError(ThumbAIException):
    """Authentication failed."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTH_ERROR")


class AuthorizationError(ThumbAIException):
    """Not authorized."""
    
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, "FORBIDDEN")


class ResourceNotFoundError(ThumbAIException):
    """Resource not found."""
    
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", "NOT_FOUND")


class ValidationError(ThumbAIException):
    """Validation failed."""
    
    def __init__(self, message: str = "Validation failed", field: Optional[str] = None):
        self.field = field
        super().__init__(message, "VALIDATION_ERROR")


class RateLimitError(ThumbAIException):
    """Rate limit exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, "RATE_LIMIT")


class InsufficientCreditsError(ThumbAIException):
    """Not enough credits."""
    
    def __init__(self, message: str = "Insufficient credits"):
        super().__init__(message, "INSUFFICIENT_CREDITS")


class AIServiceError(ThumbAIException):
    """AI service error."""
    
    def __init__(self, message: str = "AI service error"):
        super().__init__(message, "AI_ERROR")


class ImageKitError(ThumbAIException):
    """ImageKit service error."""
    
    def __init__(self, message: str = "Image upload failed"):
        super().__init__(message, "IMAGEKIT_ERROR")


class DatabaseError(ThumbAIException):
    """Database error."""
    
    def __init__(self, message: str = "Database error"):
        super().__init__(message, "DB_ERROR")


def handle_exception(exc: Exception) -> HTTPException:
    """Convert application exception to HTTPException."""
    if isinstance(exc, AuthenticationError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": exc.code, "message": exc.message}
        )
    elif isinstance(exc, AuthorizationError):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": exc.code, "message": exc.message}
        )
    elif isinstance(exc, ResourceNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": exc.code, "message": exc.message}
        )
    elif isinstance(exc, ValidationError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": exc.code, "message": exc.message, "field": exc.field}
        )
    elif isinstance(exc, RateLimitError):
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": exc.code, "message": exc.message}
        )
    elif isinstance(exc, InsufficientCreditsError):
        return HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={"error": exc.code, "message": exc.message}
        )
    elif isinstance(exc, ThumbAIException):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": exc.code, "message": exc.message}
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": "An unexpected error occurred"}
        )
