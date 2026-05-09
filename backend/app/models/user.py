"""
User Model

User account information and authentication.
"""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlmodel import SQLModel, Field, Relationship


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid4())


def now_utc() -> datetime:
    """Get current UTC datetime."""
    return datetime.utcnow()


class User(SQLModel, table=True):
    """User account model."""
    
    __tablename__ = "users"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    name: Optional[str] = Field(default=None)
    hashed_password: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(default=None)
    
    # OAuth providers
    google_id: Optional[str] = Field(default=None, index=True)
    github_id: Optional[str] = Field(default=None, index=True)
    
    # Subscription
    plan: str = Field(default="free")  # free, pro, team
    credits_remaining: int = Field(default=5)  # Daily credits
    credits_reset_at: datetime = Field(default_factory=now_utc)
    
    # Status
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)
    last_login_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    projects: List["Project"] = Relationship(back_populates="user")
    usage_records: List["Usage"] = Relationship(back_populates="user")


class UserPreferences(SQLModel, table=True):
    """User preferences and settings."""
    
    __tablename__ = "user_preferences"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    user_id: str = Field(foreign_key="users.id", unique=True)
    
    # Preferences
    default_style: str = Field(default="youtube_thumbnail")
    email_notifications: bool = Field(default=True)
    dark_mode: bool = Field(default=True)
    
    # Brand kit
    brand_primary_color: Optional[str] = Field(default=None)
    brand_font: Optional[str] = Field(default=None)
    
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)
