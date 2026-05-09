"""
Generation Service

AI thumbnail generation operations.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import uuid4
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.generation import Generation, GenerationVariant
from app.models.project import Project
from app.models.usage import Usage
from app.schemas.generation import (
    GenerationCreate, GenerateThumbnailRequest, EnhancePromptRequest,
    GenerateTitleRequest, RegenerateRequest, ExportRequest
)
from app.services.ai_service import ai_service, GrokImageSize
from app.services.imagekit_service import imagekit_service


class GenerationService:
    """Service for generation operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_generation(self, generation_id: str, user_id: str) -> Optional[Generation]:
        """Get generation by ID with user check."""
        return self.db.query(Generation).join(Project).filter(
            Generation.id == generation_id,
            Project.user_id == user_id
        ).first()
    
    def get_generations(self, user_id: str, project_id: Optional[str] = None,
                        status: Optional[str] = None, page: int = 1,
                        page_size: int = 20) -> dict:
        """Get paginated list of generations."""
        query = self.db.query(Generation).join(Project).filter(
            Project.user_id == user_id
        )
        
        if project_id:
            query = query.filter(Generation.project_id == project_id)
        
        if status:
            query = query.filter(Generation.status == status)
        
        total = query.count()
        generations = query.order_by(desc(Generation.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return {
            "items": generations,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
    
    def create_generation(self, user_id: str, request: GenerationCreate,
                          background_tasks: BackgroundTasks) -> dict:
        """Create a new generation."""
        # Get project
        project = self.db.query(Project).filter(
            Project.id == request.project_id,
            Project.user_id == user_id
        ).first()
        
        if not project:
            raise ValueError("Project not found")
        
        # Enhance prompt
        style = request.style or project.style
        enhanced_prompt = ai_service.enhance_prompt(
            project.prompt, style, project.video_title
        )
        
        # Create generation record
        generation = Generation(
            project_id=project.id,
            ai_prompt=enhanced_prompt,
            style=style,
            status="pending"
        )
        self.db.add(generation)
        self.db.commit()
        self.db.refresh(generation)
        
        # Track usage
        usage = Usage(
            user_id=user_id,
            action="generate",
            credits_used=1,
            project_id=project.id,
            generation_id=generation.id
        )
        self.db.add(usage)
        self.db.commit()
        
        # Start generation in background
        background_tasks.add_task(
            self._generate_image_task,
            generation.id,
            enhanced_prompt,
            style
        )
        
        return {
            "generation_id": generation.id,
            "status": "pending",
            "message": "Generation started"
        }
    
    def generate_direct(self, user_id: str, request: GenerateThumbnailRequest,
                        background_tasks: BackgroundTasks) -> dict:
        """Generate thumbnail directly without project."""
        # Create temporary project
        project = Project(
            user_id=user_id,
            title=request.video_title or "Direct Generation",
            prompt=request.prompt,
            style=request.style,
            video_title=request.video_title,
            headshot_url=request.headshot_url,
            status="generating"
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        
        # Enhance prompt
        enhanced_prompt = ai_service.enhance_prompt(
            request.prompt, request.style, request.video_title
        )
        
        # Create generation
        generation = Generation(
            project_id=project.id,
            ai_prompt=enhanced_prompt,
            style=request.style,
            status="pending"
        )
        self.db.add(generation)
        
        # Track usage
        usage = Usage(
            user_id=user_id,
            action="generate",
            credits_used=1,
            project_id=project.id,
            generation_id=generation.id
        )
        self.db.add(usage)
        self.db.commit()
        self.db.refresh(generation)
        
        # Start generation
        background_tasks.add_task(
            self._generate_image_task,
            generation.id,
            enhanced_prompt,
            request.style
        )
        
        return {
            "generation_id": generation.id,
            "status": "pending",
            "message": "Generation started"
        }
    
    async def _generate_image_task(self, generation_id: str, prompt: str, style: str):
        """Background task for image generation."""
        generation = self.db.query(Generation).filter(
            Generation.id == generation_id
        ).first()
        
        if not generation:
            return
        
        try:
            generation.status = "generating"
            self.db.commit()
            
            # Get appropriate size
            size = ai_service.get_size_for_style(style)
            
            # Generate image
            image_data = await ai_service.generate_image(prompt, size)
            
            if not image_data:
                raise Exception("Failed to generate image")
            
            # Upload to ImageKit
            file_name = f"thumbnail_{generation_id}_{uuid4().hex[:8]}.png"
            upload_result = imagekit_service.upload_image(
                file_bytes=image_data,
                file_name=file_name,
                folder=f"thumbnails/{generation.project_id}",
                tags=[style, "ai-generated"]
            )
            
            # Update generation
            generation.status = "completed"
            generation.image_url = upload_result["url"]
            generation.imagekit_file_id = upload_result["file_id"]
            generation.completed_at = datetime.utcnow()
            
            # Create variants
            self._create_variants(generation.id, upload_result["url"])
            
            # Score the thumbnail
            score_result = await ai_service.score_thumbnail(upload_result["url"])
            generation.ai_score = score_result["score"]
            generation.ai_feedback = score_result["feedback"]
            generation.ctr_prediction = score_result["ctr_potential"]
            
            self.db.commit()
            
        except Exception as e:
            generation.status = "failed"
            generation.error_message = str(e)
            self.db.commit()
    
    def _create_variants(self, generation_id: str, base_url: str):
        """Create platform-specific variants."""
        platforms = [
            ("youtube", 1280, 720),
            ("shorts", 1080, 1920),
            ("square", 1080, 1080),
            ("linkedin", 1200, 627)
        ]
        
        for platform, width, height in platforms:
            variant_url = imagekit_service.get_variant_url(base_url, platform)
            
            variant = GenerationVariant(
                generation_id=generation_id,
                platform=platform,
                width=width,
                height=height,
                image_url=variant_url
            )
            self.db.add(variant)
        
        self.db.commit()
    
    def get_status(self, generation_id: str, user_id: str) -> dict:
        """Get generation status."""
        generation = self.get_generation(generation_id, user_id)
        if not generation:
            raise ValueError("Generation not found")
        
        progress = 0
        if generation.status == "pending":
            progress = 10
        elif generation.status == "generating":
            progress = 50
        elif generation.status == "completed":
            progress = 100
        elif generation.status == "failed":
            progress = 0
        
        return {
            "id": generation_id,
            "status": generation.status,
            "progress": progress,
            "message": generation.error_message if generation.status == "failed" else None,
            "result": generation if generation.status == "completed" else None
        }
    
    def regenerate(self, generation_id: str, user_id: str, request: RegenerateRequest,
                   background_tasks: BackgroundTasks) -> dict:
        """Regenerate thumbnail with new parameters."""
        generation = self.get_generation(generation_id, user_id)
        if not generation:
            raise ValueError("Generation not found")
        
        project = self.db.query(Project).filter(
            Project.id == generation.project_id
        ).first()
        
        # Use new prompt or existing
        prompt = request.new_prompt or project.prompt
        style = request.new_style or generation.style
        
        # Enhance prompt
        enhanced_prompt = ai_service.enhance_prompt(prompt, style, project.video_title)
        
        # Update generation
        generation.ai_prompt = enhanced_prompt
        generation.style = style
        generation.status = "pending"
        generation.error_message = None
        self.db.commit()
        
        # Start regeneration
        background_tasks.add_task(
            self._generate_image_task,
            generation.id,
            enhanced_prompt,
            style
        )
        
        return {
            "generation_id": generation.id,
            "status": "pending",
            "message": "Regeneration started"
        }
    
    def score_thumbnail(self, generation_id: str, user_id: str) -> dict:
        """Get AI score for thumbnail."""
        generation = self.get_generation(generation_id, user_id)
        if not generation:
            raise ValueError("Generation not found")
        
        if not generation.image_url:
            raise ValueError("Generation not completed")
        
        # Return cached score or generate new
        if generation.ai_score:
            return {
                "score": generation.ai_score,
                "feedback": generation.ai_feedback or "",
                "suggestions": [],
                "ctr_potential": generation.ctr_prediction or "medium"
            }
        
        # Generate new score
        import asyncio
        score = asyncio.run(ai_service.score_thumbnail(generation.image_url))
        
        # Cache score
        generation.ai_score = score["score"]
        generation.ai_feedback = score["feedback"]
        generation.ctr_prediction = score["ctr_potential"]
        self.db.commit()
        
        return score
    
    def export_thumbnail(self, generation_id: str, user_id: str,
                         request: ExportRequest) -> dict:
        """Export thumbnail in specified format."""
        generation = self.get_generation(generation_id, user_id)
        if not generation:
            raise ValueError("Generation not found")
        
        if not generation.image_url:
            raise ValueError("Generation not completed")
        
        # Get variant for platform
        if request.platform:
            variant = self.db.query(GenerationVariant).filter(
                GenerationVariant.generation_id == generation_id,
                GenerationVariant.platform == request.platform
            ).first()
            
            if variant:
                image_url = variant.image_url
            else:
                image_url = imagekit_service.get_variant_url(
                    generation.image_url, request.platform
                )
        else:
            image_url = generation.image_url
        
        # Track usage
        usage = Usage(
            user_id=user_id,
            action="export",
            credits_used=0,
            generation_id=generation_id,
            extra_metadata=f"format:{request.format},quality:{request.quality}"
        )
        self.db.add(usage)
        self.db.commit()
        
        return {
            "download_url": image_url,
            "format": request.format,
            "file_size": 0,  # Would get actual size
            "expires_at": datetime.utcnow() + timedelta(hours=24)
        }
    
    def delete_generation(self, generation_id: str, user_id: str) -> bool:
        """Delete a generation."""
        generation = self.get_generation(generation_id, user_id)
        if not generation:
            return False
        
        # Delete from ImageKit
        if generation.imagekit_file_id:
            imagekit_service.delete_file(generation.imagekit_file_id)
        
        self.db.delete(generation)
        self.db.commit()
        return True
    
    def enhance_prompt(self, request: EnhancePromptRequest) -> dict:
        """Enhance user prompt."""
        enhanced = ai_service.enhance_prompt(
            request.prompt,
            request.style or "youtube_thumbnail",
            request.video_title
        )
        
        return {
            "original_prompt": request.prompt,
            "enhanced_prompt": enhanced,
            "suggested_styles": ["youtube_thumbnail", "mrbeast", "cinematic"],
            "suggested_text_overlays": [
                "THIS CHANGED EVERYTHING",
                "I CAN'T BELIEVE THIS",
                "YOU NEED TO SEE THIS",
                "WAIT FOR IT..."
            ]
        }
    
    def generate_titles(self, request: GenerateTitleRequest) -> dict:
        """Generate viral video titles."""
        import asyncio
        titles = asyncio.run(ai_service.generate_titles(
            request.topic,
            request.style,
            request.num_suggestions
        ))
        
        return {"suggestions": titles}
