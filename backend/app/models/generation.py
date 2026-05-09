"""
Generation Model

AI-generated thumbnails for projects.
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


class Generation(SQLModel, table=True):
    """AI thumbnail generation result."""
    
    __tablename__ = "generations"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    project_id: str = Field(foreign_key="projects.id", index=True)
    
    # Generation details
    ai_prompt: str = Field(nullable=False)
    style: str = Field(nullable=False)
    
    # Status
    status: str = Field(default="pending")  # pending, generating, completed, failed
    
    # Results
    image_url: Optional[str] = Field(default=None)
    imagekit_file_id: Optional[str] = Field(default=None)
    
    # AI Scoring
    ai_score: Optional[int] = Field(default=None)  # 0-100
    ai_feedback: Optional[str] = Field(default=None)
    
    # CTR Prediction
    ctr_prediction: Optional[float] = Field(default=None)
    
    # Error handling
    error_message: Optional[str] = Field(default=None)
    retry_count: int = Field(default=0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=now_utc)
    completed_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    project: Optional["Project"] = Relationship(back_populates="generations")


class GenerationVariant(SQLModel, table=True):
    """Different size variants of a generated thumbnail."""
    
    __tablename__ = "generation_variants"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    generation_id: str = Field(foreign_key="generations.id", index=True)
    
    # Variant details
    platform: str = Field(nullable=False)  # youtube, instagram, tiktok, linkedin
    width: int = Field(nullable=False)
    height: int = Field(nullable=False)
    
    # URLs
    image_url: str = Field(nullable=False)
    
    created_at: datetime = Field(default_factory=now_utc)
