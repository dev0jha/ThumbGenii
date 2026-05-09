"""
User Service

User management and profile operations.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User, UserPreferences
from app.models.generation import Generation
from app.models.project import Project
from app.models.usage import Usage
from app.schemas.user import UserCreate, UserUpdate, UserPreferencesUpdate


class UserService:
    """Service for user operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID."""
        return self.db.query(User).filter(User.google_id == google_id).first()
    
    def get_by_github_id(self, github_id: str) -> Optional[User]:
        """Get user by GitHub ID."""
        return self.db.query(User).filter(User.github_id == github_id).first()
    
    def create_user(self, user_data: UserCreate, hashed_password: Optional[str] = None) -> User:
        """Create a new user."""
        user = User(
            email=user_data.email,
            name=user_data.name,
            hashed_password=hashed_password,
            avatar_url=user_data.avatar_url
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Create default preferences
        prefs = UserPreferences(user_id=user.id)
        self.db.add(prefs)
        self.db.commit()
        
        return user
    
    def create_oauth_user(self, email: str, name: str, avatar_url: Optional[str],
                          provider: str, provider_id: str) -> User:
        """Create user from OAuth."""
        user_data = {"email": email, "name": name, "avatar_url": avatar_url}
        
        if provider == "google":
            user_data["google_id"] = provider_id
        elif provider == "github":
            user_data["github_id"] = provider_id
        
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Create default preferences
        prefs = UserPreferences(user_id=user.id)
        self.db.add(prefs)
        self.db.commit()
        
        return user
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user profile."""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_last_login(self, user_id: str):
        """Update last login timestamp."""
        user = self.get_by_id(user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            self.db.commit()
    
    def get_profile(self, user_id: str) -> Optional[dict]:
        """Get user profile with preferences."""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        prefs = self.db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()
        
        return {
            **user.__dict__,
            "preferences": prefs
        }
    
    def get_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Get user preferences."""
        prefs = self.db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()
        
        if not prefs:
            # Create default preferences
            prefs = UserPreferences(user_id=user_id)
            self.db.add(prefs)
            self.db.commit()
            self.db.refresh(prefs)
        
        return prefs
    
    def update_preferences(self, user_id: str, prefs_data: UserPreferencesUpdate) -> UserPreferences:
        """Update user preferences."""
        prefs = self.get_preferences(user_id)
        
        update_data = prefs_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(prefs, field, value)
        
        prefs.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(prefs)
        return prefs
    
    def get_usage_stats(self, user_id: str) -> dict:
        """Get user usage statistics."""
        # Total generations
        total = self.db.query(func.count(Generation.id)).filter(
            Generation.project_id.in_(
                self.db.query(Project.id).filter(Project.user_id == user_id)
            )
        ).scalar()
        
        # This month
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
        this_month = self.db.query(func.count(Generation.id)).filter(
            Generation.project_id.in_(
                self.db.query(Project.id).filter(Project.user_id == user_id)
            ),
            Generation.created_at >= month_start
        ).scalar()
        
        # This week
        week_start = datetime.utcnow() - timedelta(days=7)
        this_week = self.db.query(func.count(Generation.id)).filter(
            Generation.project_id.in_(
                self.db.query(Project.id).filter(Project.user_id == user_id)
            ),
            Generation.created_at >= week_start
        ).scalar()
        
        # Today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
        today = self.db.query(func.count(Generation.id)).filter(
            Generation.project_id.in_(
                self.db.query(Project.id).filter(Project.user_id == user_id)
            ),
            Generation.created_at >= today_start
        ).scalar()
        
        # Credits used today
        credits_today = self.db.query(func.coalesce(func.sum(Usage.credits_used), 0)).filter(
            Usage.user_id == user_id,
            Usage.created_at >= today_start
        ).scalar()
        
        user = self.get_by_id(user_id)
        
        return {
            "total_generations": total,
            "generations_this_month": this_month,
            "generations_this_week": this_week,
            "generations_today": today,
            "credits_remaining": user.credits_remaining if user else 0,
            "credits_used_today": credits_today,
            "plan": user.plan if user else "free",
            "plan_expires_at": None
        }
    
    def get_analytics(self, user_id: str) -> dict:
        """Get user analytics summary."""
        # Total projects
        total_projects = self.db.query(func.count(Project.id)).filter(
            Project.user_id == user_id
        ).scalar()
        
        # Total generations
        total_generations = self.db.query(func.count(Generation.id)).filter(
            Generation.project_id.in_(
                self.db.query(Project.id).filter(Project.user_id == user_id)
            )
        ).scalar()
        
        # Average AI score
        avg_score = self.db.query(func.avg(Generation.ai_score)).filter(
            Generation.project_id.in_(
                self.db.query(Project.id).filter(Project.user_id == user_id)
            ),
            Generation.ai_score.isnot(None)
        ).scalar()
        
        # Favorite style
        style_counts = self.db.query(
            Project.style, func.count(Project.id)
        ).filter(
            Project.user_id == user_id
        ).group_by(Project.style).all()
        
        favorite_style = max(style_counts, key=lambda x: x[1])[0] if style_counts else None
        
        # Generations by style
        generations_by_style = {style: count for style, count in style_counts}
        
        # Generations by month (last 6 months)
        months = []
        for i in range(6):
            month_start = (datetime.utcnow() - timedelta(days=30*i)).replace(day=1)
            month_count = self.db.query(func.count(Generation.id)).filter(
                Generation.project_id.in_(
                    self.db.query(Project.id).filter(Project.user_id == user_id)
                ),
                Generation.created_at >= month_start,
                Generation.created_at < month_start + timedelta(days=30)
            ).scalar()
            months.append({
                "month": month_start.strftime("%Y-%m"),
                "count": month_count
            })
        
        return {
            "total_projects": total_projects,
            "total_generations": total_generations,
            "average_ai_score": round(avg_score, 1) if avg_score else None,
            "favorite_style": favorite_style,
            "generations_by_style": generations_by_style,
            "generations_by_month": months
        }
    
    def use_credits(self, user_id: str, amount: int = 1) -> bool:
        """Deduct credits from user."""
        user = self.get_by_id(user_id)
        if not user or user.credits_remaining < amount:
            return False
        
        user.credits_remaining -= amount
        self.db.commit()
        return True
    
    def reset_daily_credits(self, user_id: str, daily_limit: int = 5):
        """Reset daily credits for free users."""
        user = self.get_by_id(user_id)
        if user and user.plan == "free":
            # Check if credits need reset
            if user.credits_reset_at.date() < datetime.utcnow().date():
                user.credits_remaining = daily_limit
                user.credits_reset_at = datetime.utcnow()
                self.db.commit()
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user and all associated data."""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True
