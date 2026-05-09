"""
User Schemas

Pydantic models for user-related API requests and responses.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """User update schema."""
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """User response schema."""
    id: str
    plan: str
    credits_remaining: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserProfileResponse(UserResponse):
    """Extended user profile with preferences."""
    preferences: Optional["UserPreferencesResponse"] = None


class UserPreferencesBase(BaseModel):
    """Base user preferences schema."""
    default_style: str = "youtube_thumbnail"
    email_notifications: bool = True
    dark_mode: bool = True
    brand_primary_color: Optional[str] = None
    brand_font: Optional[str] = None


class UserPreferencesUpdate(BaseModel):
    """User preferences update schema."""
    default_style: Optional[str] = None
    email_notifications: Optional[bool] = None
    dark_mode: Optional[bool] = None
    brand_primary_color: Optional[str] = None
    brand_font: Optional[str] = None


class UserPreferencesResponse(UserPreferencesBase):
    """User preferences response schema."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


class OAuthLoginRequest(BaseModel):
    """OAuth login request schema."""
    provider: str  # google, github
    code: str
    redirect_uri: str


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    """Change password request schema."""
    current_password: str
    new_password: str = Field(..., min_length=8)
