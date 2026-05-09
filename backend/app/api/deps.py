"""
API Dependencies

Common dependencies for API routes.
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user_id, get_optional_user_id
from app.services.user_service import UserService


def get_db_session() -> Generator[Session, None, None]:
    """Get database session dependency."""
    yield from get_db()


def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db_session)
):
    """Get current authenticated user."""
    user_service = UserService(db)
    user = user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


def get_optional_user(
    user_id: Optional[str] = Depends(get_optional_user_id),
    db: Session = Depends(get_db_session)
):
    """Get optional authenticated user."""
    if not user_id:
        return None
    user_service = UserService(db)
    return user_service.get_by_id(user_id)


def require_active_user(
    user = Depends(get_current_user)
):
    """Require active user."""
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    return user


def require_pro_plan(
    user = Depends(get_current_user)
):
    """Require Pro or higher plan."""
    if user.plan not in ["pro", "team"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pro plan required for this feature"
        )
    return user


def check_credits(
    user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Check if user has available credits."""
    if user.credits_remaining <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="No credits remaining. Please upgrade your plan."
        )
    return user
