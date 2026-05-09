"""
Common Schemas

Shared Pydantic models used across the API.
"""

from typing import Optional, List, TypeVar, Generic
from pydantic import BaseModel


T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination query parameters."""
    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    message: str
    details: Optional[dict] = None
    code: Optional[str] = None


class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = True
    message: str
    data: Optional[dict] = None


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str
    services: dict


class APIInfoResponse(BaseModel):
    """API information response."""
    name: str
    version: str
    description: str
    documentation_url: str
    endpoints: List[dict]


class UsageStatsResponse(BaseModel):
    """Usage statistics response."""
    total_generations: int
    generations_this_month: int
    generations_this_week: int
    generations_today: int
    credits_remaining: int
    credits_used_today: int
    plan: str
    plan_expires_at: Optional[str] = None


class AnalyticsSummaryResponse(BaseModel):
    """Analytics summary response."""
    total_projects: int
    total_generations: int
    average_ai_score: Optional[float] = None
    favorite_style: Optional[str] = None
    generations_by_style: dict
    generations_by_month: list
