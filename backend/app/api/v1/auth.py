"""
Authentication API Routes

User registration, login, and OAuth endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, get_current_user
from app.schemas.user import (
    UserCreate, UserResponse, LoginRequest, TokenResponse,
    RefreshTokenRequest, OAuthLoginRequest, PasswordResetRequest,
    PasswordResetConfirm, ChangePasswordRequest
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db_session)
):
    """Register a new user account."""
    auth_service = AuthService(db)
    return auth_service.register(user_data)


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db_session)
):
    """Login with email and password."""
    auth_service = AuthService(db)
    return auth_service.login(credentials.email, credentials.password)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db_session)
):
    """Refresh access token using refresh token."""
    auth_service = AuthService(db)
    return auth_service.refresh_token(request.refresh_token)


@router.post("/oauth/{provider}", response_model=TokenResponse)
def oauth_login(
    provider: str,
    request: OAuthLoginRequest,
    db: Session = Depends(get_db_session)
):
    """Login with OAuth provider (google, github)."""
    auth_service = AuthService(db)
    return auth_service.oauth_login(provider, request.code, request.redirect_uri)


@router.post("/logout")
def logout(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Logout current user."""
    auth_service = AuthService(db)
    auth_service.logout(current_user.id)
    return {"message": "Successfully logged out"}


@router.post("/password-reset")
def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db_session)
):
    """Request password reset email."""
    auth_service = AuthService(db)
    auth_service.request_password_reset(request.email)
    return {"message": "Password reset email sent if account exists"}


@router.post("/password-reset/confirm")
def confirm_password_reset(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db_session)
):
    """Confirm password reset with token."""
    auth_service = AuthService(db)
    auth_service.reset_password(request.token, request.new_password)
    return {"message": "Password reset successful"}


@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Change current user password."""
    auth_service = AuthService(db)
    auth_service.change_password(
        current_user.id,
        request.current_password,
        request.new_password
    )
    return {"message": "Password changed successfully"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Get current authenticated user information."""
    return current_user
