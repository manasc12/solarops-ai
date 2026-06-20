"""Forecast endpoints. Routes only — all logic lives in ForecastService."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.app.models.requests import ForecastRequest
from backend.app.models.responses import APIResponse
from backend.app.services.forecast_service import get_forecast_service

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.post("", response_model=APIResponse)
def create_forecast(req: ForecastRequest) -> APIResponse:
    try:
        forecast = get_forecast_service().generate(req.farm_id, req.horizon_hours)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return APIResponse.ok(forecast.model_dump())


@router.get("/{farm_id}", response_model=APIResponse)
def latest_forecast(farm_id: str) -> APIResponse:
    forecast = get_forecast_service().get_latest(farm_id)
    if forecast is None:
        raise HTTPException(status_code=404, detail=f"No forecast for farm {farm_id}")
    return APIResponse.ok(forecast.model_dump())
