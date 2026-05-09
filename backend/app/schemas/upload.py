"""
Upload Schemas

Pydantic models for file upload-related API requests and responses.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """File upload response schema."""
    success: bool
    file_id: str
    url: str
    file_name: str
    file_size: int
    content_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class UploadPresignedRequest(BaseModel):
    """Presigned URL upload request."""
    file_name: str
    content_type: str = Field(..., pattern="^(image/jpeg|image/png|image/webp)$")
    file_size: int = Field(..., le=10 * 1024 * 1024)  # 10MB max


class UploadPresignedResponse(BaseModel):
    """Presigned URL upload response."""
    upload_url: str
    file_id: str
    expires_at: datetime


class ImageProcessingRequest(BaseModel):
    """Image processing request."""
    image_url: str
    operations: list = Field(..., description="List of operations: resize, crop, enhance, remove_bg")


class ImageProcessingResponse(BaseModel):
    """Image processing response."""
    processed_url: str
    original_url: str
    operations_applied: list


class ImageMetadataResponse(BaseModel):
    """Image metadata response."""
    url: str
    width: int
    height: int
    format: str
    file_size: int
    color_space: Optional[str] = None
    has_transparency: bool = False
