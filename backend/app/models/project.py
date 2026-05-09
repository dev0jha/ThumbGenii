"""
Project Model

Thumbnail projects created by users.
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


class Project(SQLModel, table=True):
    """Thumbnail project model."""
    
    __tablename__ = "projects"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    
    # Project details
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    
    # AI Generation inputs
    prompt: str = Field(nullable=False)
    style: str = Field(default="youtube_thumbnail")
    video_title: Optional[str] = Field(default=None)
    
    # Uploaded assets
    headshot_url: Optional[str] = Field(default=None)
    logo_url: Optional[str] = Field(default=None)
    reference_image_url: Optional[str] = Field(default=None)
    
    # Status
    status: str = Field(default="draft")  # draft, generating, completed, failed
    
    # Timestamps
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="projects")
    generations: List["Generation"] = Relationship(back_populates="project")


class ProjectTemplate(SQLModel, table=True):
    """Pre-built thumbnail templates."""
    
    __tablename__ = "project_templates"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    name: str = Field(nullable=False)
    category: str = Field(nullable=False)  # gaming, finance, podcast, etc.
    description: Optional[str] = Field(default=None)
    
    # Template settings
    style_preset: str = Field(nullable=False)
    prompt_template: str = Field(nullable=False)
    
    # Preview
    preview_url: Optional[str] = Field(default=None)
    
    # Metadata
    is_premium: bool = Field(default=False)
    is_active: bool = Field(default=True)
    usage_count: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=now_utc)
