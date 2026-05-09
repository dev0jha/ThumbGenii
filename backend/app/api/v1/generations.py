"""
Generations API Routes

AI thumbnail generation endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, get_current_user, check_credits
from app.schemas.generation import (
    GenerationCreate, GenerationResponse, GenerationDetailResponse,
    GenerationListResponse, GenerateThumbnailRequest, GenerateThumbnailResponse,
    EnhancePromptRequest, EnhancePromptResponse, GenerateTitleRequest,
    GenerateTitleResponse, AIScoreResponse, RegenerateRequest,
    ExportRequest, ExportResponse, GenerationStatusResponse
)
from app.services.generation_service import GenerationService

router = APIRouter(prefix="/generations", tags=["Generations"])


@router.get("", response_model=GenerationListResponse)
def list_generations(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """List generations with optional filtering."""
    generation_service = GenerationService(db)
    return generation_service.get_generations(
        user_id=current_user.id,
        project_id=project_id,
        status=status,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=GenerateThumbnailResponse, status_code=status.HTTP_202_ACCEPTED)
def create_generation(
    request: GenerationCreate,
    background_tasks: BackgroundTasks,
    current_user = Depends(check_credits),
    db: Session = Depends(get_db_session)
):
    """Create a new AI generation for a project."""
    generation_service = GenerationService(db)
    return generation_service.create_generation(
        user_id=current_user.id,
        request=request,
        background_tasks=background_tasks
    )


@router.post("/generate", response_model=GenerateThumbnailResponse, status_code=status.HTTP_202_ACCEPTED)
def generate_thumbnail(
    request: GenerateThumbnailRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(check_credits),
    db: Session = Depends(get_db_session)
):
    """Generate thumbnail directly without creating a project first."""
    generation_service = GenerationService(db)
    return generation_service.generate_direct(
        user_id=current_user.id,
        request=request,
        background_tasks=background_tasks
    )


@router.get("/{generation_id}", response_model=GenerationDetailResponse)
def get_generation(
    generation_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get generation details with variants."""
    generation_service = GenerationService(db)
    generation = generation_service.get_generation(generation_id, current_user.id)
    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found"
        )
    return generation


@router.get("/{generation_id}/status", response_model=GenerationStatusResponse)
def get_generation_status(
    generation_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Check generation status and progress."""
    generation_service = GenerationService(db)
    return generation_service.get_status(generation_id, current_user.id)


@router.post("/{generation_id}/regenerate", response_model=GenerateThumbnailResponse)
def regenerate_thumbnail(
    generation_id: str,
    request: RegenerateRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(check_credits),
    db: Session = Depends(get_db_session)
):
    """Regenerate an existing thumbnail with new parameters."""
    generation_service = GenerationService(db)
    return generation_service.regenerate(
        generation_id=generation_id,
        user_id=current_user.id,
        request=request,
        background_tasks=background_tasks
    )


@router.post("/{generation_id}/score", response_model=AIScoreResponse)
def score_thumbnail(
    generation_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get AI score and feedback for a thumbnail."""
    generation_service = GenerationService(db)
    return generation_service.score_thumbnail(generation_id, current_user.id)


@router.post("/{generation_id}/export", response_model=ExportResponse)
def export_thumbnail(
    generation_id: str,
    request: ExportRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Export thumbnail in specified format."""
    generation_service = GenerationService(db)
    return generation_service.export_thumbnail(
        generation_id=generation_id,
        user_id=current_user.id,
        request=request
    )


@router.delete("/{generation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_generation(
    generation_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Delete a generation."""
    generation_service = GenerationService(db)
    success = generation_service.delete_generation(generation_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found"
        )
    return None


# AI Enhancement endpoints

@router.post("/ai/enhance-prompt", response_model=EnhancePromptResponse)
def enhance_prompt(
    request: EnhancePromptRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Enhance user prompt with AI."""
    generation_service = GenerationService(db)
    return generation_service.enhance_prompt(request)


@router.post("/ai/generate-title", response_model=GenerateTitleResponse)
def generate_title(
    request: GenerateTitleRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Generate viral video titles with AI."""
    generation_service = GenerationService(db)
    return generation_service.generate_titles(request)
