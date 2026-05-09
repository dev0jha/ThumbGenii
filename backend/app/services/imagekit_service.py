"""
ImageKit Service

CDN integration for image storage and optimization.
"""

import logging
from typing import Optional, Dict
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

from app.core.config import settings

logger = logging.getLogger("thumbai.imagekit")


class ImageKitService:
    """Service for ImageKit CDN operations."""
    
    def __init__(self):
        self.client = None
        if all([settings.IMAGEKIT_PRIVATE_KEY, settings.IMAGEKIT_PUBLIC_KEY, settings.IMAGEKIT_URL_ENDPOINT]):
            self.client = ImageKit(
                private_key=settings.IMAGEKIT_PRIVATE_KEY,
                public_key=settings.IMAGEKIT_PUBLIC_KEY,
                url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
            )
    
    def upload_image(
        self,
        file_bytes: bytes,
        file_name: str,
        folder: str = "thumbnails",
        content_type: str = "image/png",
        tags: Optional[list] = None
    ) -> Dict:
        """Upload image to ImageKit CDN."""
        if not self.client:
            raise ValueError("ImageKit not configured")
        
        options = UploadFileRequestOptions(
            folder=folder,
            is_private_file=False,
            use_unique_file_name=True,
            tags=tags or []
        )
        
        result = self.client.upload_file(
            file=(file_bytes, content_type, file_name),
            file_name=file_name,
            options=options
        )
        
        return {
            "file_id": result.file_id,
            "url": result.url,
            "thumbnail_url": result.thumbnail_url,
            "file_name": result.name,
            "file_path": result.file_path,
            "size": result.size
        }
    
    def get_variant_url(self, base_url: str, platform: str = "youtube") -> str:
        """Get platform-optimized image URL."""
        transformations = {
            "youtube": "tr=w-1280,h-720,c-maintain_ratio,fo-auto",
            "shorts": "tr=w-1080,h-1920,c-maintain_ratio,fo-auto",
            "square": "tr=w-1080,h-1080,c-maintain_ratio,fo-auto",
            "instagram": "tr=w-1080,h-1080,c-maintain_ratio,fo-auto",
            "tiktok": "tr=w-1080,h-1920,c-maintain_ratio,fo-auto",
            "linkedin": "tr=w-1200,h-627,c-maintain_ratio,fo-auto",
            "thumbnail": "tr=w-300,h-300,c-maintain_ratio,fo-auto",
        }
        
        transform = transformations.get(platform, transformations["youtube"])
        separator = "?" if "?" not in base_url else "&"
        return f"{base_url}{separator}{transform}"
    
    def delete_file(self, file_id: str) -> bool:
        """Delete file from ImageKit."""
        if not self.client:
            return False
        
        try:
            self.client.delete_file(file_id)
            return True
        except Exception as e:
            logger.error("Error deleting file %s: %s", file_id, e)
            return False
    
    def get_file_metadata(self, file_id: str) -> Optional[Dict]:
        """Get file metadata from ImageKit."""
        if not self.client:
            return None
        
        try:
            result = self.client.get_file_details(file_id)
            return {
                "file_id": result.file_id,
                "name": result.name,
                "url": result.url,
                "size": result.size,
                "width": result.width,
                "height": result.height,
                "format": result.file_type or result.mime,
                "created_at": result.created_at
            }
        except Exception as e:
            logger.error("Error getting file metadata for %s: %s", file_id, e)
            return None
    
    def generate_upload_url(self, file_name: str, folder: str = "uploads") -> Dict:
        """Generate presigned upload URL."""
        if not self.client:
            raise ValueError("ImageKit not configured")
        
        # ImageKit doesn't support presigned URLs directly
        # Return upload endpoint info
        return {
            "upload_url": f"{settings.IMAGEKIT_URL_ENDPOINT}/api/v1/files/upload",
            "folder": folder,
            "public_key": settings.IMAGEKIT_PUBLIC_KEY
        }


# Singleton instance
imagekit_service = ImageKitService()
