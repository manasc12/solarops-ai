"""Farm registry endpoints (read-only)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.app.db.repository import FarmRepository
from backend.app.models.responses import APIResponse

router = APIRouter(prefix="/farms", tags=["farms"])


@router.get("", response_model=APIResponse)
def list_farms() -> APIResponse:
    farms = FarmRepository().list()
    return APIResponse.ok([f.model_dump() for f in farms])


@router.get("/{farm_id}", response_model=APIResponse)
def get_farm(farm_id: str) -> APIResponse:
    farm = FarmRepository().get(farm_id)
    if farm is None:
        raise HTTPException(status_code=404, detail=f"Unknown farm_id: {farm_id}")
    return APIResponse.ok(farm.model_dump())
