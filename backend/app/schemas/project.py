"""
Project Schemas

Pydantic models for project-related API requests and responses.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base project schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    prompt: str = Field(..., min_length=1, max_length=2000)
    style: str = "youtube_thumbnail"
    video_title: Optional[str] = Field(None, max_length=200)


class ProjectCreate(ProjectBase):
    """Project creation schema."""
    headshot_url: Optional[str] = None
    logo_url: Optional[str] = None
    reference_image_url: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Project update schema."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    prompt: Optional[str] = Field(None, min_length=1, max_length=2000)
    style: Optional[str] = None
    video_title: Optional[str] = Field(None, max_length=200)


class ProjectResponse(ProjectBase):
    """Project response schema."""
    id: str
    user_id: str
    status: str
    headshot_url: Optional[str] = None
    logo_url: Optional[str] = None
    reference_image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    """Project with generations."""
    generations: List["GenerationResponse"] = []


class ProjectListResponse(BaseModel):
    """Paginated project list response."""
    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ProjectTemplateResponse(BaseModel):
    """Project template response schema."""
    id: str
    name: str
    category: str
    description: Optional[str] = None
    style_preset: str
    prompt_template: str
    preview_url: Optional[str] = None
    is_premium: bool
    is_active: bool
    usage_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectFromTemplateRequest(BaseModel):
    """Create project from template request."""
    template_id: str
    title: str = Field(..., min_length=1, max_length=200)
    customizations: Optional[dict] = None


class ThumbnailStyle(BaseModel):
    """Thumbnail style definition."""
    id: str
    name: str
    description: str
    aspect_ratio: str
    recommended_platforms: List[str]
    preview_url: Optional[str] = None


class ThumbnailStylesResponse(BaseModel):
    """Available thumbnail styles response."""
    styles: List[ThumbnailStyle]


# Supported styles constant
SUPPORTED_STYLES = [
    "youtube_thumbnail",
    "shorts",
    "square",
    "cinematic",
    "minimalist",
    "gaming",
    "tutorial",
    "mrbeast",
    "finance",
    "podcast",
    "documentary",
    "anime",
    "tech",
    "educational",
    "dark_theme",
    "viral_shorts"
]


STYLE_INFO = {
    "youtube_thumbnail": {
        "name": "YouTube Thumbnail",
        "description": "Standard 16:9 YouTube thumbnail with bold text",
        "aspect_ratio": "16:9",
        "recommended_platforms": ["youtube"],
        "dimensions": {"width": 1280, "height": 720}
    },
    "shorts": {
        "name": "Shorts/Reels",
        "description": "Vertical 9:16 format for short-form video",
        "aspect_ratio": "9:16",
        "recommended_platforms": ["youtube_shorts", "tiktok", "instagram_reels"],
        "dimensions": {"width": 1080, "height": 1920}
    },
    "square": {
        "name": "Square",
        "description": "1:1 square format for social media",
        "aspect_ratio": "1:1",
        "recommended_platforms": ["instagram", "facebook"],
        "dimensions": {"width": 1080, "height": 1080}
    },
    "cinematic": {
        "name": "Cinematic",
        "description": "Movie poster style with dramatic lighting",
        "aspect_ratio": "16:9",
        "recommended_platforms": ["youtube", "vimeo"],
        "dimensions": {"width": 1280, "height": 720}
    },
    "minimalist": {
        "name": "Minimalist",
        "description": "Clean, simple design with minimal elements",
        "aspect_ratio": "16:9",
        "recommended_platforms": ["youtube", "linkedin"],
        "dimensions": {"width": 1280, "height": 720}
    },
    "gaming": {
        "name": "Gaming",
        "description": "High-energy gaming thumbnail style",
        "aspect_ratio": "16:9",
        "recommended_platforms": ["youtube"],
        "dimensions": {"width": 1280, "height": 720}
    },
    "tutorial": {
        "name": "Tutorial",
        "description": "Educational content with clear visuals",
        "aspect_ratio": "16:9",
        "recommended_platforms": ["youtube"],
        "dimensions": {"width": 1280, "height": 720}
    },
    "mrbeast": {
        "name": "MrBeast Style",
        "description": "High contrast, shocked expression, bright colors",
        "aspect_ratio": "16:9",
        "recommended_platforms": ["youtube"],
        "dimensions": {"width": 1280, "height": 720}
    },
    "finance": {
        "name": "Finance",
        "description": "Professional financial content style",
        "aspect_ratio": "16:9",
        "recommended_platforms": ["youtube", "linkedin"],
        "dimensions": {"width": 1280, "height": 720}
    },
    "podcast": {
        "name": "Podcast",
        "description": "Podcast cover style with host imagery",
        "aspect_ratio": "1:1",
        "recommended_platforms": ["spotify", "apple_podcasts", "youtube"],
        "dimensions": {"width": 1080, "height": 1080}
    },
    "documentary": {
        "name": "Documentary",
        "description": "Serious, informative documentary style",
        "aspect_ratio": "16:9",
        "recommended_platforms": ["youtube", "vimeo"],
        "dimensions": {"width": 1280, "height": 720}
    },
    "anime": {
        "name": "Anime",
        "description": "Anime/manga inspired thumbnail style",
        "aspect_ratio": "16:9",
        "recommended_platforms": ["youtube"],
        "dimensions": {"width": 1280, "height": 720}
    },
    "tech": {
        "name": "Tech",
        "description": "Technology review and showcase style",
        "aspect_ratio": "16:9",
        "recommended_platforms": ["youtube"],
        "dimensions": {"width": 1280, "height": 720}
    },
    "educational": {
        "name": "Educational",
        "description": "Learning and knowledge content style",
        "aspect_ratio": "16:9",
        "recommended_platforms": ["youtube"],
        "dimensions": {"width": 1280, "height": 720}
    },
    "dark_theme": {
        "name": "Dark Theme",
        "description": "Dark background with neon accents",
        "aspect_ratio": "16:9",
        "recommended_platforms": ["youtube"],
        "dimensions": {"width": 1280, "height": 720}
    },
    "viral_shorts": {
        "name": "Viral Shorts",
        "description": "Attention-grabbing vertical format",
        "aspect_ratio": "9:16",
        "recommended_platforms": ["youtube_shorts", "tiktok"],
        "dimensions": {"width": 1080, "height": 1920}
    }
}
