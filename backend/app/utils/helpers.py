"""
Helpers

General utility functions.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid4())


def generate_short_id(length: int = 8) -> str:
    """Generate a short random ID."""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_api_key() -> str:
    """Generate a secure API key."""
    prefix = "thai_"
    chars = string.ascii_letters + string.digits
    key = ''.join(random.choices(chars, k=32))
    return prefix + key


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime to ISO string."""
    if dt is None:
        return None
    return dt.isoformat()


def parse_datetime(date_string: str) -> Optional[datetime]:
    """Parse ISO datetime string."""
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None


def get_relative_time(dt: datetime) -> str:
    """Get human-readable relative time."""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff < timedelta(minutes=1):
        return "just now"
    elif diff < timedelta(hours=1):
        minutes = int(diff.seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff < timedelta(days=1):
        hours = int(diff.seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff < timedelta(days=7):
        days = diff.days
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        return dt.strftime("%b %d, %Y")


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def generate_random_color() -> str:
    """Generate random hex color."""
    return '#' + ''.join(random.choices('0123456789ABCDEF', k=6))


def is_valid_hex_color(color: str) -> bool:
    """Check if string is valid hex color."""
    if not color.startswith('#'):
        return False
    return len(color) == 7 and all(c in '0123456789ABCDEFabcdef' for c in color[1:])


def chunk_list(lst: list, chunk_size: int):
    """Split list into chunks."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def deep_merge(dict1: dict, dict2: dict) -> dict:
    """Deep merge two dictionaries."""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
