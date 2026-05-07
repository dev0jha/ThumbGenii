"""
Grok Image Generation Service

This module handles AI-powered image generation using xAI's Grok API
and manages the upload of generated images to ImageKit storage.
"""

import os
import httpx
import base64
from typing import Optional, List
from datetime import datetime
from uuid import uuid4

from sqlmodel import Session, select

from config import GROK_API_KEY
from database import engine
from models import Job, Thumbnail
from services.imagekit_service import upload_image


# Grok API configuration
GROK_API_BASE_URL = "https://api.x.ai/v1"


def generate_image_prompt(base_prompt: str, style: str = "youtube_thumbnail") -> str:
    """
    Enhance the user prompt with style-specific instructions for better thumbnail generation.
    
    Args:
        base_prompt: The user's original prompt
        style: The style of thumbnail (youtube_thumbnail, shorts, square)
    
    Returns:
        Enhanced prompt optimized for thumbnail generation
    """
    style_instructions = {
        "youtube_thumbnail": (
            "Create a high-quality YouTube thumbnail image. "
            "The image should be eye-catching, vibrant, and designed to attract clicks. "
            "Use bold colors, clear focal points, and professional composition. "
            "Style: Modern, engaging, high contrast, suitable for 1280x720 display. "
        ),
        "shorts": (
            "Create a high-quality YouTube Shorts thumbnail image. "
            "The image should be vertical, mobile-optimized, and attention-grabbing. "
            "Use bold text elements, vibrant colors, and clear subject. "
            "Style: Vertical format, mobile-friendly, punchy and dynamic. "
        ),
        "square": (
            "Create a high-quality square thumbnail image. "
            "The image should be balanced, professional, and suitable for social media. "
            "Use centered composition, clear visuals, and appealing aesthetics. "
            "Style: Square format, balanced composition, versatile for multiple platforms. "
        ),
        "cinematic": (
            "Create a cinematic movie poster style thumbnail. "
            "Use dramatic lighting, epic composition, and Hollywood-style aesthetics. "
            "Style: Cinematic, dramatic, professional movie poster quality. "
        ),
        "minimalist": (
            "Create a clean, minimalist thumbnail design. "
            "Use simple shapes, ample negative space, and elegant typography. "
            "Style: Minimalist, clean, modern, sophisticated. "
        ),
        "gaming": (
            "Create an energetic gaming thumbnail. "
            "Use neon colors, dynamic action poses, and gaming aesthetics. "
            "Style: Gaming, energetic, bold, high-impact visuals. "
        ),
        "tutorial": (
            "Create an educational tutorial thumbnail. "
            "Use clear visuals, friendly colors, and approachable design. "
            "Style: Educational, friendly, clear and informative. "
        ),
    }
    
    style_text = style_instructions.get(style, style_instructions["youtube_thumbnail"])
    
    enhanced_prompt = f"{style_text}Subject: {base_prompt}. "
    enhanced_prompt += "High quality, professional, no text overlays, photorealistic or stylized as appropriate."
    
    return enhanced_prompt


def generate_image_with_grok(
    prompt: str,
    size: str = "1024x1024"
) -> Optional[bytes]:
    """
    Generate an image using xAI's Grok API.
    
    Args:
        prompt: The image generation prompt
        size: Image size (1024x1024, 1024x1792, 1792x1024)
    
    Returns:
        Image data as bytes, or None if generation failed
    """
    try:
        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "grok-2-image",
            "prompt": prompt,
            "n": 1,
            "size": size,
            "response_format": "b64_json"
        }
        
        response = httpx.post(
            f"{GROK_API_BASE_URL}/images/generations",
            headers=headers,
            json=payload,
            timeout=60.0
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Decode base64 image data
        if "data" in data and len(data["data"]) > 0:
            image_data = base64.b64decode(data["data"][0]["b64_json"])
            return image_data
        
        return None
        
    except Exception as e:
        print(f"Error generating image with Grok: {str(e)}")
        return None


def create_thumbnail_for_job(
    job_id: str,
    style: str = "youtube_thumbnail"
) -> Optional[Thumbnail]:
    """
    Generate a thumbnail image for a job and save it to the database.
    
    Args:
        job_id: The ID of the job
        style: The thumbnail style
    
    Returns:
        The created Thumbnail object, or None if failed
    """
    with Session(engine) as session:
        # Get the job
        statement = select(Job).where(Job.id == job_id)
        job = session.exec(statement).first()
        
        if not job:
            print(f"Job {job_id} not found")
            return None
        
        # Create thumbnail record
        thumbnail = Thumbnail(
            job_id=job_id,
            style=style,
            status="generating"
        )
        session.add(thumbnail)
        session.commit()
        session.refresh(thumbnail)
        
        try:
            # Generate enhanced prompt
            enhanced_prompt = generate_image_prompt(job.prompt, style)
            
            # Determine size based on style
            size_map = {
                "youtube_thumbnail": "1792x1024",  # Landscape
                "shorts": "1024x1792",              # Portrait
                "square": "1024x1024",              # Square
            }
            size = size_map.get(style, "1024x1024")
            
            # Generate image using Grok
            image_data = generate_image_with_grok(
                prompt=enhanced_prompt,
                size=size
            )
            
            if not image_data:
                raise Exception("Failed to generate image with Grok API")
            
            # Generate unique filename
            file_name = f"thumbnail_{job_id}_{uuid4().hex[:8]}.png"
            folder = f"thumbnails/{job_id}"
            
            # Upload to ImageKit
            image_url = upload_image(
                file_bytes=image_data,
                file_name=file_name,
                folder=folder,
                content_type="image/png"
            )
            
            # Update thumbnail record
            thumbnail.status = "completed"
            thumbnail.image_url = image_url
            session.add(thumbnail)
            session.commit()
            session.refresh(thumbnail)
            
            return thumbnail
            
        except Exception as e:
            # Update thumbnail with error status
            thumbnail.status = "failed"
            thumbnail.error_message = str(e)
            session.add(thumbnail)
            session.commit()
            session.refresh(thumbnail)
            
            print(f"Error creating thumbnail for job {job_id}: {str(e)}")
            return None


def generate_multiple_thumbnails(
    job_id: str,
    styles: List[str]
) -> List[Thumbnail]:
    """
    Generate multiple thumbnails with different styles for a single job.
    
    Args:
        job_id: The ID of the job
        styles: List of styles to generate
    
    Returns:
        List of created Thumbnail objects
    """
    thumbnails = []
    
    for style in styles:
        thumbnail = create_thumbnail_for_job(job_id, style)
        if thumbnail:
            thumbnails.append(thumbnail)
    
    return thumbnails


def regenerate_thumbnail(
    thumbnail_id: int,
    new_prompt: Optional[str] = None,
    new_style: Optional[str] = None
) -> Optional[Thumbnail]:
    """
    Regenerate an existing thumbnail with optional new parameters.
    
    Args:
        thumbnail_id: The ID of the thumbnail to regenerate
        new_prompt: Optional new prompt (uses job's prompt if None)
        new_style: Optional new style (uses existing style if None)
    
    Returns:
        The regenerated Thumbnail object, or None if failed
    """
    with Session(engine) as session:
        # Get existing thumbnail
        statement = select(Thumbnail).where(Thumbnail.id == thumbnail_id)
        thumbnail = session.exec(statement).first()
        
        if not thumbnail:
            print(f"Thumbnail {thumbnail_id} not found")
            return None
        
        # Get associated job
        statement = select(Job).where(Job.id == thumbnail.job_id)
        job = session.exec(statement).first()
        
        if not job:
            print(f"Job for thumbnail {thumbnail_id} not found")
            return None
        
        # Update status to regenerating
        thumbnail.status = "regenerating"
        session.add(thumbnail)
        session.commit()
        
        try:
            # Use new values or fall back to existing
            prompt = new_prompt if new_prompt else job.prompt
            style = new_style if new_style else thumbnail.style
            
            # Generate enhanced prompt
            enhanced_prompt = generate_image_prompt(prompt, style)
            
            # Determine size
            size_map = {
                "youtube_thumbnail": "1792x1024",
                "shorts": "1024x1792",
                "square": "1024x1024",
            }
            size = size_map.get(style, "1024x1024")
            
            # Generate image using Grok
            image_data = generate_image_with_grok(
                prompt=enhanced_prompt,
                size=size
            )
            
            if not image_data:
                raise Exception("Failed to regenerate image with Grok API")
            
            # Generate new filename
            file_name = f"thumbnail_{thumbnail.job_id}_{uuid4().hex[:8]}.png"
            folder = f"thumbnails/{thumbnail.job_id}"
            
            # Upload to ImageKit
            image_url = upload_image(
                file_bytes=image_data,
                file_name=file_name,
                folder=folder,
                content_type="image/png"
            )
            
            # Update thumbnail record
            thumbnail.status = "completed"
            thumbnail.style = style
            thumbnail.image_url = image_url
            thumbnail.error_message = None
            session.add(thumbnail)
            session.commit()
            session.refresh(thumbnail)
            
            return thumbnail
            
        except Exception as e:
            thumbnail.status = "failed"
            thumbnail.error_message = str(e)
            session.add(thumbnail)
            session.commit()
            
            print(f"Error regenerating thumbnail {thumbnail_id}: {str(e)}")
            return None


def get_thumbnail_by_id(thumbnail_id: int) -> Optional[Thumbnail]:
    """
    Retrieve a thumbnail by its ID.
    
    Args:
        thumbnail_id: The ID of the thumbnail
    
    Returns:
        The Thumbnail object, or None if not found
    """
    with Session(engine) as session:
        statement = select(Thumbnail).where(Thumbnail.id == thumbnail_id)
        return session.exec(statement).first()


def get_thumbnails_by_job(job_id: str) -> List[Thumbnail]:
    """
    Retrieve all thumbnails for a specific job.
    
    Args:
        job_id: The ID of the job
    
    Returns:
        List of Thumbnail objects
    """
    with Session(engine) as session:
        statement = select(Thumbnail).where(Thumbnail.job_id == job_id)
        return session.exec(statement).all()


def delete_thumbnail(thumbnail_id: int) -> bool:
    """
    Delete a thumbnail from the database.
    
    Args:
        thumbnail_id: The ID of the thumbnail to delete
    
    Returns:
        True if deleted successfully, False otherwise
    """
    with Session(engine) as session:
        statement = select(Thumbnail).where(Thumbnail.id == thumbnail_id)
        thumbnail = session.exec(statement).first()
        
        if thumbnail:
            session.delete(thumbnail)
            session.commit()
            return True
        
        return False


# Example usage and testing
if __name__ == "__main__":
    # Test prompt generation
    test_prompt = "A developer coding on a laptop with coffee"
    enhanced = generate_image_prompt(test_prompt, "youtube_thumbnail")
    print(f"Enhanced prompt: {enhanced}\n")
    
    # Test image generation (requires valid API key)
    print("Testing image generation with Grok API...")
    image_data = generate_image_with_grok(
        prompt="A simple test image of a red apple on a white background",
        size="1024x1024"
    )
    
    if image_data:
        print(f"Image generated successfully! Size: {len(image_data)} bytes")
    else:
        print("Image generation failed")
