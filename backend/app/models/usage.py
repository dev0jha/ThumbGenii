"""
Usage Model

Track user credit consumption and analytics.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlmodel import SQLModel, Field, Relationship


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid4())


def now_utc() -> datetime:
    """Get current UTC datetime."""
    return datetime.utcnow()


class Usage(SQLModel, table=True):
    """Usage tracking for billing and analytics."""
    
    __tablename__ = "usage"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    
    # Usage details
    action: str = Field(nullable=False)  # generate, enhance, upload, export
    credits_used: int = Field(default=1)
    
    # Related entities
    project_id: Optional[str] = Field(default=None)
    generation_id: Optional[str] = Field(default=None)
    
    # Metadata
    extra_metadata: Optional[str] = Field(default=None)  # JSON string
    
    # Timestamps
    created_at: datetime = Field(default_factory=now_utc)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="usage_records")


class DailyUsageStats(SQLModel, table=True):
    """Aggregated daily usage statistics."""
    
    __tablename__ = "daily_usage_stats"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    date: datetime = Field(index=True)
    
    # Totals
    total_generations: int = Field(default=0)
    total_users: int = Field(default=0)
    total_credits_used: int = Field(default=0)
    
    # Success rates
    successful_generations: int = Field(default=0)
    failed_generations: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=now_utc)
