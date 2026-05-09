"""
Health Check API Routes

System health and status endpoints.
"""

from datetime import datetime
from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import HealthCheckResponse, APIInfoResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheckResponse)
def health_check():
    """Check system health status."""
    return HealthCheckResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow().isoformat(),
        services={
            "database": "connected",
            "ai_service": "connected",
            "cdn": "connected"
        }
    )


@router.get("/health/ready")
def readiness_check():
    """Kubernetes readiness probe."""
    return {"status": "ready"}


@router.get("/health/live")
def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}


@router.get("/api-info", response_model=APIInfoResponse)
def api_info():
    """Get API information."""
    return APIInfoResponse(
        name=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-powered thumbnail generation API",
        documentation_url="/docs",
        endpoints=[
            {"path": "/api/v1/auth", "description": "Authentication"},
            {"path": "/api/v1/users", "description": "User management"},
            {"path": "/api/v1/projects", "description": "Project management"},
            {"path": "/api/v1/generations", "description": "AI generation"},
            {"path": "/api/v1/uploads", "description": "File uploads"},
        ]
    )
