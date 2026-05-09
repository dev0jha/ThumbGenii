"""
Users API Routes

User profile and preferences endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, get_current_user
from app.schemas.user import (
    UserUpdate, UserResponse, UserProfileResponse,
    UserPreferencesUpdate, UserPreferencesResponse
)
from app.schemas.common import UsageStatsResponse, AnalyticsSummaryResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResponse)
def get_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get current user profile with preferences."""
    user_service = UserService(db)
    return user_service.get_profile(current_user.id)


@router.put("/me", response_model=UserResponse)
def update_profile(
    user_data: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Update user profile."""
    user_service = UserService(db)
    return user_service.update_user(current_user.id, user_data)


@router.get("/me/preferences", response_model=UserPreferencesResponse)
def get_preferences(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get user preferences."""
    user_service = UserService(db)
    return user_service.get_preferences(current_user.id)


@router.put("/me/preferences", response_model=UserPreferencesResponse)
def update_preferences(
    prefs_data: UserPreferencesUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Update user preferences."""
    user_service = UserService(db)
    return user_service.update_preferences(current_user.id, prefs_data)


@router.get("/me/stats", response_model=UsageStatsResponse)
def get_usage_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get user usage statistics."""
    user_service = UserService(db)
    return user_service.get_usage_stats(current_user.id)


@router.get("/me/analytics", response_model=AnalyticsSummaryResponse)
def get_analytics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get user analytics summary."""
    user_service = UserService(db)
    return user_service.get_analytics(current_user.id)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Delete user account and all data."""
    user_service = UserService(db)
    user_service.delete_user(current_user.id)
    return None
