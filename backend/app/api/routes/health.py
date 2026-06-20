"""Health and readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.core.config import settings
from backend.app.models.responses import APIResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=APIResponse)
def health() -> APIResponse:
    return APIResponse.ok(
        {
            "service": settings.app_name,
            "env": settings.app_env,
            "status": "healthy",
        }
    )
