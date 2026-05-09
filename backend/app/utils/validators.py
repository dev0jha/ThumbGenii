"""
Validators

Input validation utilities.
"""

import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """Validate password strength.
    
    Returns:
        (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, None


def validate_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return bool(re.match(pattern, url))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove path components
    filename = filename.replace("..", "").replace("/", "").replace("\\", "")
    # Remove special characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    return filename.strip()


def validate_image_type(content_type: str) -> bool:
    """Validate image content type."""
    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    return content_type in allowed


def validate_image_size(size_bytes: int, max_size_mb: int = 10) -> bool:
    """Validate image file size."""
    max_bytes = max_size_mb * 1024 * 1024
    return size_bytes <= max_bytes
