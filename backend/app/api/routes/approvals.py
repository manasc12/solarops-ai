"""Approval (human-in-the-loop) endpoints. Routes only — logic in ApprovalService."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.app.models.requests import ApprovalDecisionRequest, ApprovalSubmitRequest
from backend.app.models.responses import APIResponse
from backend.app.models.schemas import ApprovalStatus
from backend.app.services.approval_service import get_approval_service

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.post("", response_model=APIResponse)
def submit_approval(req: ApprovalSubmitRequest) -> APIResponse:
    try:
        request = get_approval_service().submit(
            farm_id=req.farm_id,
            action_type=req.action_type,
            severity=req.severity,
            description=req.description,
            proposed_by=req.proposed_by,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return APIResponse.ok(request.model_dump())


@router.post("/decision", response_model=APIResponse)
def decide_approval(req: ApprovalDecisionRequest) -> APIResponse:
    try:
        decision = ApprovalStatus(req.decision.upper())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid decision: {req.decision}") from exc
    if decision not in {ApprovalStatus.APPROVED, ApprovalStatus.REJECTED, ApprovalStatus.MODIFIED}:
        raise HTTPException(status_code=400, detail="Decision must be APPROVED/REJECTED/MODIFIED")
    try:
        request = get_approval_service().decide(
            request_id=req.request_id, decision=decision, reviewer=req.reviewer, notes=req.notes
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return APIResponse.ok(request.model_dump())


@router.get("", response_model=APIResponse)
def list_pending() -> APIResponse:
    pending = get_approval_service().list_pending()
    return APIResponse.ok([r.model_dump() for r in pending])


@router.get("/all", response_model=APIResponse)
def list_all() -> APIResponse:
    items = get_approval_service().list_all()
    return APIResponse.ok([r.model_dump() for r in items])


@router.get("/{request_id}", response_model=APIResponse)
def get_approval(request_id: str) -> APIResponse:
    request = get_approval_service().get(request_id)
    if request is None:
        raise HTTPException(status_code=404, detail=f"Unknown approval request: {request_id}")
    history = get_approval_service().decision_history(request_id)
    return APIResponse.ok(
        {"request": request.model_dump(), "history": [d.model_dump() for d in history]}
    )
