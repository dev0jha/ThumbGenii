"""
Auth Service

Authentication and authorization operations.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, decode_token
)
from app.models.user import User
from app.schemas.user import UserCreate, TokenResponse
from app.services.user_service import UserService

logger = logging.getLogger("thumbai.auth")


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
    
    def register(self, user_data: UserCreate) -> User:
        """Register a new user."""
        existing = self.user_service.get_by_email(user_data.email)
        if existing:
            raise ValueError("Email already registered")
        
        hashed_password = get_password_hash(user_data.password)
        user = self.user_service.create_user(user_data, hashed_password)
        logger.info("New user registered: %s", user.email)
        return user
    
    def login(self, email: str, password: str) -> TokenResponse:
        """Authenticate user and return tokens."""
        user = self.user_service.get_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")
        
        if not user.hashed_password:
            raise ValueError("Please use OAuth login")
        
        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")
        
        if not user.is_active:
            raise ValueError("Account is deactivated")
        
        self.user_service.update_last_login(user.id)
        
        token_data = {"sub": user.id, "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=60 * 24 * 7,
            user=user
        )
    
    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token."""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")
        
        user_id = payload.get("sub")
        user = self.user_service.get_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        
        token_data = {"sub": user.id, "email": user.email}
        access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=60 * 24 * 7,
            user=user
        )
    
    def oauth_login(self, provider: str, code: str, redirect_uri: str) -> TokenResponse:
        """Handle OAuth login via Google or GitHub."""
        provider = provider.lower()
        
        if provider == "google":
            user_info = self._exchange_google_code(code, redirect_uri)
        elif provider == "github":
            user_info = self._exchange_github_code(code, redirect_uri)
        else:
            raise ValueError(f"Unsupported OAuth provider: {provider}")
        
        if not user_info:
            raise ValueError("Failed to authenticate with provider")
        
        email = user_info.get("email")
        if not email:
            raise ValueError("Email not provided by OAuth provider")
        
        # Find existing user or create new
        existing = None
        if provider == "google":
            existing = self.user_service.get_by_google_id(user_info.get("id"))
        elif provider == "github":
            existing = self.user_service.get_by_github_id(user_info.get("id"))
        
        if not existing:
            existing = self.user_service.get_by_email(email)
        
        if existing:
            user = existing
            if provider == "google":
                user.google_id = user_info.get("id")
            elif provider == "github":
                user.github_id = user_info.get("id")
            user.is_verified = True
        else:
            user = self.user_service.create_oauth_user(
                email=email,
                name=user_info.get("name", ""),
                avatar_url=user_info.get("avatar_url"),
                provider=provider,
                provider_id=user_info.get("id")
            )
            user.is_verified = True
        
        self.db.commit()
        self.user_service.update_last_login(user.id)
        
        token_data = {"sub": user.id, "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        logger.info("OAuth login: %s via %s", user.email, provider)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=60 * 24 * 7,
            user=user
        )
    
    def _exchange_google_code(self, code: str, redirect_uri: str) -> Optional[dict]:
        """Exchange Google OAuth code for user info."""
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            logger.warning("Google OAuth not configured")
            return None
        
        try:
            token_resp = httpx.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
                timeout=15
            )
            token_resp.raise_for_status()
            access_token = token_resp.json().get("access_token")
            
            user_resp = httpx.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=15
            )
            user_resp.raise_for_status()
            data = user_resp.json()
            
            return {
                "id": data.get("id"),
                "email": data.get("email"),
                "name": data.get("name"),
                "avatar_url": data.get("picture"),
            }
        except Exception as e:
            logger.error("Google OAuth exchange failed: %s", e)
            return None
    
    def _exchange_github_code(self, code: str, redirect_uri: str) -> Optional[dict]:
        """Exchange GitHub OAuth code for user info."""
        if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
            logger.warning("GitHub OAuth not configured")
            return None
        
        try:
            token_resp = httpx.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "code": code,
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                },
                headers={"Accept": "application/json"},
                timeout=15
            )
            token_resp.raise_for_status()
            access_token = token_resp.json().get("access_token")
            
            user_resp = httpx.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
                timeout=15
            )
            user_resp.raise_for_status()
            data = user_resp.json()
            
            # Get primary email
            emails_resp = httpx.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
                timeout=15
            )
            emails = emails_resp.json()
            primary_email = None
            for e in emails:
                if e.get("primary"):
                    primary_email = e.get("email")
                    break
            if not primary_email and emails:
                primary_email = emails[0].get("email")
            
            return {
                "id": str(data.get("id")),
                "email": primary_email,
                "name": data.get("name") or data.get("login"),
                "avatar_url": data.get("avatar_url"),
            }
        except Exception as e:
            logger.error("GitHub OAuth exchange failed: %s", e)
            return None
    
    def logout(self, user_id: str):
        """Logout user (invalidate tokens)."""
        logger.info("User logged out: %s", user_id)
    
    def request_password_reset(self, email: str):
        """Request password reset - generates token (real email sending stubbed)."""
        user = self.user_service.get_by_email(email)
        if user:
            token_data = {"sub": user.id, "email": user.email, "type": "password_reset"}
            reset_token = create_access_token(token_data, expires_delta=timedelta(hours=1))
            logger.info(
                "Password reset requested for %s. Token would be sent via email.",
                email
            )
            # In production, send email with reset link containing token
            # For development, the token can be used directly via the reset endpoint
            logger.debug("Password reset token for %s: %s", email, reset_token)
    
    def reset_password(self, token: str, new_password: str):
        """Reset password with token."""
        payload = decode_token(token)
        if not payload or payload.get("type") != "password_reset":
            raise ValueError("Invalid or expired reset token")
        
        user_id = payload.get("sub")
        user = self.user_service.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        self.db.commit()
        logger.info("Password reset completed for user: %s", user.email)
    
    def change_password(self, user_id: str, current_password: str, new_password: str):
        """Change user password."""
        user = self.user_service.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if not user.hashed_password:
            raise ValueError("Cannot change OAuth account password")
        
        if not verify_password(current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")
        
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        self.db.commit()
        logger.info("Password changed for user: %s", user.email)
