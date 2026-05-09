"""
Project Service

Project management operations.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.project import Project, ProjectTemplate
from app.models.generation import Generation
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectFromTemplateRequest


class ProjectService:
    """Service for project operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_project(self, project_id: str, user_id: str) -> Optional[Project]:
        """Get project by ID with user check."""
        return self.db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
    
    def get_user_projects(self, user_id: str, page: int = 1, page_size: int = 20,
                          status: Optional[str] = None) -> dict:
        """Get paginated list of user projects."""
        query = self.db.query(Project).filter(Project.user_id == user_id)
        
        if status:
            query = query.filter(Project.status == status)
        
        total = query.count()
        projects = query.order_by(desc(Project.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return {
            "items": projects,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
    
    def create_project(self, user_id: str, project_data: ProjectCreate) -> Project:
        """Create a new project."""
        project = Project(
            user_id=user_id,
            title=project_data.title,
            description=project_data.description,
            prompt=project_data.prompt,
            style=project_data.style,
            video_title=project_data.video_title,
            headshot_url=project_data.headshot_url,
            logo_url=project_data.logo_url,
            reference_image_url=project_data.reference_image_url,
            status="draft"
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def update_project(self, project_id: str, user_id: str,
                       project_data: ProjectUpdate) -> Optional[Project]:
        """Update project details."""
        project = self.get_project(project_id, user_id)
        if not project:
            return None
        
        update_data = project_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        project.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def delete_project(self, project_id: str, user_id: str) -> bool:
        """Delete a project and its generations."""
        project = self.get_project(project_id, user_id)
        if not project:
            return False
        
        # Delete associated generations
        self.db.query(Generation).filter(
            Generation.project_id == project_id
        ).delete()
        
        self.db.delete(project)
        self.db.commit()
        return True
    
    def duplicate_project(self, project_id: str, user_id: str) -> Optional[Project]:
        """Duplicate an existing project."""
        project = self.get_project(project_id, user_id)
        if not project:
            return None
        
        new_project = Project(
            user_id=user_id,
            title=f"{project.title} (Copy)",
            description=project.description,
            prompt=project.prompt,
            style=project.style,
            video_title=project.video_title,
            headshot_url=project.headshot_url,
            logo_url=project.logo_url,
            reference_image_url=project.reference_image_url,
            status="draft"
        )
        self.db.add(new_project)
        self.db.commit()
        self.db.refresh(new_project)
        return new_project
    
    def get_templates(self, category: Optional[str] = None) -> List[ProjectTemplate]:
        """Get available project templates."""
        query = self.db.query(ProjectTemplate).filter(
            ProjectTemplate.is_active == True
        )
        
        if category:
            query = query.filter(ProjectTemplate.category == category)
        
        return query.order_by(ProjectTemplate.usage_count.desc()).all()
    
    def create_from_template(self, user_id: str,
                             request: ProjectFromTemplateRequest) -> Project:
        """Create project from template."""
        template = self.db.query(ProjectTemplate).filter(
            ProjectTemplate.id == request.template_id
        ).first()
        
        if not template:
            raise ValueError("Template not found")
        
        # Apply customizations to template
        prompt = template.prompt_template
        if request.customizations:
            for key, value in request.customizations.items():
                prompt = prompt.replace(f"{{{key}}}", str(value))
        
        project = Project(
            user_id=user_id,
            title=request.title,
            prompt=prompt,
            style=template.style_preset,
            status="draft"
        )
        self.db.add(project)
        
        # Update template usage count
        template.usage_count += 1
        
        self.db.commit()
        self.db.refresh(project)
        return project
