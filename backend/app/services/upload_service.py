"""
Upload Service

File upload and image processing operations.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.services.imagekit_service import imagekit_service

logger = logging.getLogger("thumbai.upload")


class UploadService:
    """Service for upload operations."""
    
    ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
    MAX_SIZE = 10 * 1024 * 1024
    
    def __init__(self, db: Session):
        self.db = db
    
    def upload_file(self, file: UploadFile, user_id: str,
                    folder: str = "uploads") -> dict:
        """Upload file to ImageKit."""
        if file.content_type not in self.ALLOWED_TYPES:
            raise ValueError(f"Invalid file type: {file.content_type}")
        
        contents = file.file.read()
        
        if len(contents) > self.MAX_SIZE:
            raise ValueError(f"File too large: {len(contents)} bytes (max {self.MAX_SIZE})")
        
        ext = file.filename.split(".")[-1] if "." in file.filename else "png"
        file_name = f"{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
        
        result = imagekit_service.upload_image(
            file_bytes=contents,
            file_name=file_name,
            folder=f"{folder}/{user_id}",
            content_type=file.content_type
        )
        
        logger.info("File uploaded: %s (%d bytes)", file_name, len(contents))
        
        return {
            "success": True,
            "file_id": result["file_id"],
            "url": result["url"],
            "file_name": file_name,
            "file_size": len(contents),
            "content_type": file.content_type,
            "uploaded_at": datetime.utcnow()
        }
    
    def get_presigned_url(self, file_name: str, content_type: str,
                          file_size: int, user_id: str) -> dict:
        """Get presigned upload URL."""
        if content_type not in self.ALLOWED_TYPES:
            raise ValueError(f"Invalid file type: {content_type}")
        
        if file_size > self.MAX_SIZE:
            raise ValueError(f"File too large: {file_size} bytes")
        
        result = imagekit_service.generate_upload_url(file_name, f"uploads/{user_id}")
        
        return {
            "upload_url": result["upload_url"],
            "file_id": f"pending_{user_id}_{datetime.utcnow().timestamp()}",
            "expires_at": datetime.utcnow() + timedelta(minutes=15)
        }
    
    def process_image(self, image_url: str, operations: list,
                    user_id: str) -> dict:
        """Process image using ImageKit transformations."""
        processed_url = image_url
        
        for op in operations:
            if op == "resize":
                processed_url = self._apply_transform(processed_url, "w-800,h-450,c-maintain_ratio")
            elif op == "crop":
                processed_url = self._apply_transform(processed_url, "c-maintain_ratio,fo-auto")
            elif op == "enhance":
                processed_url = self._apply_transform(processed_url, "e-sharpen:5,e-contrast:10,e-brightness:5")
            elif op == "remove_bg":
                processed_url = self._apply_transform(processed_url, "e-background-removal")
        
        logger.info("Image processed: %s operations=%s", image_url, operations)
        
        return {
            "processed_url": processed_url,
            "original_url": image_url,
            "operations_applied": operations
        }
    
    def _apply_transform(self, url: str, transform: str) -> str:
        """Apply an ImageKit transformation to a URL."""
        separator = "?" if "?" not in url else "&"
        return f"{url}{separator}tr={transform}"
    
    def get_metadata(self, image_url: str) -> dict:
        """Get image metadata."""
        if imagekit_service.client:
            try:
                file_id = image_url.split("/")[-1].split(".")[0]
                meta = imagekit_service.get_file_metadata(file_id)
                if meta:
                    return {
                        "url": image_url,
                        "width": meta.get("width", 1280),
                        "height": meta.get("height", 720),
                        "format": meta.get("format", "png"),
                        "file_size": meta.get("size", 0),
                        "color_space": "RGB",
                        "has_transparency": True
                    }
            except Exception as e:
                logger.warning("Failed to fetch metadata from ImageKit: %s", e)
        
        return {
            "url": image_url,
            "width": 1280,
            "height": 720,
            "format": "png",
            "file_size": 0,
            "color_space": "RGB",
            "has_transparency": True
        }
    
    def remove_background(self, image_url: str, user_id: str) -> dict:
        """Remove background using ImageKit transformation."""
        processed_url = self._apply_transform(image_url, "e-background-removal")
        
        file_name = f"bg_removed_{user_id}_{uuid.uuid4().hex[:8]}.png"
        
        logger.info("Background removed: %s", image_url)
        
        return {
            "success": True,
            "file_id": f"bg_removed_{user_id}",
            "url": processed_url,
            "file_name": file_name,
            "file_size": 0,
            "content_type": "image/png",
            "uploaded_at": datetime.utcnow()
        }
    
    def enhance_image(self, image_url: str, user_id: str) -> dict:
        """Enhance image using ImageKit transformations."""
        processed_url = self._apply_transform(
            image_url,
            "e-sharpen:5,e-contrast:10,e-brightness:5,e-improve"
        )
        
        file_name = f"enhanced_{user_id}_{uuid.uuid4().hex[:8]}.png"
        
        logger.info("Image enhanced: %s", image_url)
        
        return {
            "success": True,
            "file_id": f"enhanced_{user_id}",
            "url": processed_url,
            "file_name": file_name,
            "file_size": 0,
            "content_type": "image/png",
            "uploaded_at": datetime.utcnow()
        }
