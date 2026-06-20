"""API request models. Explicit, validated inputs for every endpoint."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from backend.app.models.schemas import ActionType, Severity


class ForecastRequest(BaseModel):
    farm_id: str
    horizon_hours: int = Field(default=24, ge=1, le=168)
    target_date: Optional[datetime] = None


class AnomalyRequest(BaseModel):
    farm_id: str
    lookback_hours: int = Field(default=24, ge=1, le=168)


class RCARequest(BaseModel):
    farm_id: str


class ReportRequest(BaseModel):
    farm_id: str


class ApprovalSubmitRequest(BaseModel):
    farm_id: str
    action_type: ActionType
    severity: Severity
    description: str
    proposed_by: str = "system"


class ApprovalDecisionRequest(BaseModel):
    request_id: str
    decision: str
    reviewer: str
    notes: Optional[str] = None


class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = Field(default=4, ge=1, le=20)


class PipelineRunRequest(BaseModel):
    farm_id: str
