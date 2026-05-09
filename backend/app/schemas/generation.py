"""
Generation Schemas

Pydantic models for AI generation-related API requests and responses.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class GenerationBase(BaseModel):
    """Base generation schema."""
    ai_prompt: str
    style: str


class GenerationCreate(BaseModel):
    """Generation creation request schema."""
    project_id: str
    style: Optional[str] = None  # Uses project style if not specified
    num_variations: int = Field(default=1, ge=1, le=4)


class GenerationResponse(BaseModel):
    """Generation response schema."""
    id: str
    project_id: str
    ai_prompt: str
    style: str
    status: str
    image_url: Optional[str] = None
    ai_score: Optional[int] = None
    ai_feedback: Optional[str] = None
    ctr_prediction: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class GenerationDetailResponse(GenerationResponse):
    """Generation with variants."""
    variants: List["GenerationVariantResponse"] = []


class GenerationVariantResponse(BaseModel):
    """Generation variant response schema."""
    id: str
    generation_id: str
    platform: str
    width: int
    height: int
    image_url: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class GenerationListResponse(BaseModel):
    """Paginated generation list response."""
    items: List[GenerationResponse]
    total: int
    page: int
    page_size: int
    pages: int


class GenerateThumbnailRequest(BaseModel):
    """Direct thumbnail generation request."""
    prompt: str = Field(..., min_length=1, max_length=2000)
    style: str = "youtube_thumbnail"
    video_title: Optional[str] = Field(None, max_length=200)
    headshot_url: Optional[str] = None
    num_variations: int = Field(default=1, ge=1, le=4)


class GenerateThumbnailResponse(BaseModel):
    """Direct thumbnail generation response."""
    generation_id: str
    status: str
    message: str


class AIScoreResponse(BaseModel):
    """AI thumbnail scoring response."""
    score: int = Field(..., ge=0, le=100)
    feedback: str
    suggestions: List[str]
    ctr_potential: str  # low, medium, high, viral


class EnhancePromptRequest(BaseModel):
    """Prompt enhancement request."""
    prompt: str = Field(..., min_length=1, max_length=1000)
    style: Optional[str] = None
    video_title: Optional[str] = None


class EnhancePromptResponse(BaseModel):
    """Prompt enhancement response."""
    original_prompt: str
    enhanced_prompt: str
    suggested_styles: List[str]
    suggested_text_overlays: List[str]


class GenerateTitleRequest(BaseModel):
    """AI title generation request."""
    topic: str = Field(..., min_length=1, max_length=500)
    style: Optional[str] = None
    num_suggestions: int = Field(default=5, ge=1, le=10)


class GenerateTitleResponse(BaseModel):
    """AI title generation response."""
    suggestions: List[str]


class RegenerateRequest(BaseModel):
    """Regenerate thumbnail request."""
    generation_id: str
    new_prompt: Optional[str] = None
    new_style: Optional[str] = None


class ExportRequest(BaseModel):
    """Export thumbnail request."""
    generation_id: str
    format: str = Field(default="png", pattern="^(png|jpg|webp)$")
    quality: int = Field(default=90, ge=50, le=100)
    platform: Optional[str] = None  # youtube, instagram, tiktok, linkedin


class ExportResponse(BaseModel):
    """Export thumbnail response."""
    download_url: str
    format: str
    file_size: int
    expires_at: datetime


class GenerationStatusResponse(BaseModel):
    """Generation status check response."""
    id: str
    status: str
    progress: int = Field(..., ge=0, le=100)
    message: Optional[str] = None
    result: Optional[GenerationResponse] = None
