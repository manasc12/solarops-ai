"""Report & pipeline endpoints. Routes only — orchestration lives in workflows."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.app.db.repository import ReportRepository
from backend.app.models.requests import PipelineRunRequest, ReportRequest
from backend.app.models.responses import APIResponse
from workflows.daily_operations_graph import run_daily_operations

router = APIRouter(tags=["reports"])


@router.post("/report", response_model=APIResponse)
def generate_report(req: ReportRequest) -> APIResponse:
    """Run the full daily-operations workflow and return its report + state."""
    try:
        state = run_daily_operations(req.farm_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return APIResponse.ok(
        {
            "farm_id": state.farm_id,
            "report": state.report,
            "approval_status": state.approval_status.value,
            "anomaly": state.anomaly.model_dump() if state.anomaly else None,
            "forecast": state.forecast.model_dump() if state.forecast else None,
            "rca": state.rca.model_dump() if state.rca else None,
            "trace": state.metadata.get("trace", []),
        }
    )


@router.get("/report/{farm_id}", response_model=APIResponse)
def latest_report(farm_id: str) -> APIResponse:
    report = ReportRepository().get(farm_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"No report for farm {farm_id}")
    return APIResponse.ok({"farm_id": farm_id, "report": report})


@router.post("/pipeline/run", response_model=APIResponse)
def run_pipeline(req: PipelineRunRequest) -> APIResponse:
    """Alias for the full workflow run, returning the final structured state."""
    try:
        state = run_daily_operations(req.farm_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return APIResponse.ok(state.model_dump())
