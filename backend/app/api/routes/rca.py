"""Root cause analysis endpoints. Routes only — logic lives in RCAService."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.app.models.requests import RCARequest
from backend.app.models.responses import APIResponse
from backend.app.services.rca_service import get_rca_service

router = APIRouter(prefix="/rca", tags=["rca"])


@router.post("", response_model=APIResponse)
def run_rca(req: RCARequest) -> APIResponse:
    try:
        result = get_rca_service().analyze(req.farm_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return APIResponse.ok(result.model_dump())


@router.get("/{farm_id}", response_model=APIResponse)
def latest_rca(farm_id: str) -> APIResponse:
    result = get_rca_service().get_latest(farm_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No RCA for farm {farm_id}")
    return APIResponse.ok(result.model_dump())
