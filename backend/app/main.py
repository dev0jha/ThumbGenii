"""
ThumbAI FastAPI Application

Main entry point for the FastAPI application.
"""

import logging
import time
from collections import defaultdict
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logger import setup_logging
from app.db.session import init_db
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.projects import router as projects_router
from app.api.v1.generations import router as generations_router
from app.api.v1.uploads import router as uploads_router
from app.api.v1.health import router as health_router

logger = logging.getLogger("thumbai")

# In-memory rate limiter
_rate_limit_store: dict = defaultdict(list)


def _is_rate_limited(client_id: str, max_requests: int, window_seconds: int = 60) -> bool:
    now = time.time()
    window_start = now - window_seconds
    timestamps = _rate_limit_store[client_id]
    # Prune old entries
    _rate_limit_store[client_id] = [t for t in timestamps if t > window_start]
    if len(_rate_limit_store[client_id]) >= max_requests:
        return True
    _rate_limit_store[client_id].append(now)
    return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_logging()
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    _rate_limit_store.clear()
    logger.info("Shutting down...")


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="AI-powered thumbnail generation API",
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # Rate limiting middleware
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        if _is_rate_limited(client_ip, settings.RATE_LIMIT_PER_MINUTE):
            return JSONResponse(
                status_code=429,
                content={"error": "RATE_LIMIT", "message": "Too many requests"}
            )
        return await call_next(request)

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Gzip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        from app.utils.exceptions import handle_exception
        http_exc = handle_exception(exc)
        return JSONResponse(
            status_code=http_exc.status_code,
            content=http_exc.detail
        )
    
    # Include routers
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(projects_router, prefix="/api/v1")
    app.include_router(generations_router, prefix="/api/v1")
    app.include_router(uploads_router, prefix="/api/v1")
    
    return app


# Create application instance
app = create_application()


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "api": "/api/v1"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
