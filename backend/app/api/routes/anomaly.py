"""Anomaly endpoints. Routes only — logic lives in AnomalyService."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.app.models.requests import AnomalyRequest
from backend.app.models.responses import APIResponse
from backend.app.services.anomaly_service import get_anomaly_service

router = APIRouter(prefix="/anomaly", tags=["anomaly"])


@router.post("", response_model=APIResponse)
def detect_anomaly(req: AnomalyRequest) -> APIResponse:
    try:
        result = get_anomaly_service().detect(req.farm_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return APIResponse.ok(result.model_dump())


@router.get("/{farm_id}", response_model=APIResponse)
def latest_anomaly(farm_id: str) -> APIResponse:
    result = get_anomaly_service().get_latest(farm_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No anomaly result for farm {farm_id}")
    return APIResponse.ok(result.model_dump())
