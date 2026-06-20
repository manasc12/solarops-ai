"""Aggregate API router wiring all route modules under /api/v1."""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.routes import (
    anomaly,
    approvals,
    farms,
    forecast,
    health,
    rag,
    rca,
    reports,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(farms.router)
api_router.include_router(forecast.router)
api_router.include_router(anomaly.router)
api_router.include_router(rca.router)
api_router.include_router(approvals.router)
api_router.include_router(reports.router)
api_router.include_router(rag.router)
