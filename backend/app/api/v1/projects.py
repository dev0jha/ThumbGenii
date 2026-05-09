"""
Projects API Routes

Project management endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, get_current_user, check_credits
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetailResponse,
    ProjectListResponse, ProjectTemplateResponse, ProjectFromTemplateRequest
)
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=ProjectListResponse)
def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """List user's projects with pagination."""
    project_service = ProjectService(db)
    return project_service.get_user_projects(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Create a new thumbnail project."""
    project_service = ProjectService(db)
    return project_service.create_project(current_user.id, project_data)


@router.get("/templates", response_model=List[ProjectTemplateResponse])
def list_templates(
    category: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """List available project templates."""
    project_service = ProjectService(db)
    return project_service.get_templates(category=category)


@router.post("/from-template", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_from_template(
    request: ProjectFromTemplateRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Create a project from a template."""
    project_service = ProjectService(db)
    return project_service.create_from_template(current_user.id, request)


@router.get("/styles")
def get_styles(
    current_user = Depends(get_current_user)
):
    """Get available thumbnail styles."""
    from app.schemas.project import STYLE_INFO
    return {"styles": STYLE_INFO}


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project(
    project_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get project details with generations."""
    project_service = ProjectService(db)
    project = project_service.get_project(project_id, current_user.id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Update project details."""
    project_service = ProjectService(db)
    project = project_service.update_project(project_id, current_user.id, project_data)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Delete a project and its generations."""
    project_service = ProjectService(db)
    success = project_service.delete_project(project_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return None


@router.post("/{project_id}/duplicate", response_model=ProjectResponse)
def duplicate_project(
    project_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Duplicate an existing project."""
    project_service = ProjectService(db)
    project = project_service.duplicate_project(project_id, current_user.id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project
