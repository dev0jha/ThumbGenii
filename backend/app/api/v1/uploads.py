"""
Uploads API Routes

File upload and image processing endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, get_current_user
from app.schemas.upload import (
    UploadResponse, UploadPresignedRequest, UploadPresignedResponse,
    ImageProcessingRequest, ImageProcessingResponse, ImageMetadataResponse
)
from app.services.upload_service import UploadService

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("/image", response_model=UploadResponse)
def upload_image(
    file: UploadFile = File(...),
    folder: str = "uploads",
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Upload an image file."""
    upload_service = UploadService(db)
    return upload_service.upload_file(
        file=file,
        user_id=current_user.id,
        folder=folder
    )


@router.post("/presigned", response_model=UploadPresignedResponse)
def get_presigned_url(
    request: UploadPresignedRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get presigned URL for direct upload."""
    upload_service = UploadService(db)
    return upload_service.get_presigned_url(
        file_name=request.file_name,
        content_type=request.content_type,
        file_size=request.file_size,
        user_id=current_user.id
    )


@router.post("/process", response_model=ImageProcessingResponse)
def process_image(
    request: ImageProcessingRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Process an image with various operations."""
    upload_service = UploadService(db)
    return upload_service.process_image(
        image_url=request.image_url,
        operations=request.operations,
        user_id=current_user.id
    )


@router.get("/metadata", response_model=ImageMetadataResponse)
def get_image_metadata(
    image_url: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get image metadata."""
    upload_service = UploadService(db)
    return upload_service.get_metadata(image_url)


@router.post("/remove-background", response_model=UploadResponse)
def remove_background(
    image_url: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Remove background from image."""
    upload_service = UploadService(db)
    return upload_service.remove_background(
        image_url=image_url,
        user_id=current_user.id
    )


@router.post("/enhance", response_model=UploadResponse)
def enhance_image(
    image_url: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Enhance image quality."""
    upload_service = UploadService(db)
    return upload_service.enhance_image(
        image_url=image_url,
        user_id=current_user.id
    )
