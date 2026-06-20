"""Canonical data contracts for SolarOps AI.

This module is the SINGLE SOURCE OF TRUTH for all data structures, mirroring
`.github/data_schema.md` exactly. Every layer (API, agents, ML, RAG, workflows)
imports its schemas from here. No free-form dictionaries may cross module
boundaries.

Schema version: v1
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

SCHEMA_VERSION = "v1"


# ── Enumerations ────────────────────────────────────────────────────────────
class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class InverterStatus(str, Enum):
    OK = "OK"
    DEGRADED = "DEGRADED"
    FAILURE = "FAILURE"


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"


class ActionType(str, Enum):
    WORK_ORDER = "WorkOrder"
    ALERT = "Alert"
    SHUTDOWN = "Shutdown"


class DetectionMethod(str, Enum):
    ISOLATION_FOREST = "IsolationForest"
    STATISTICAL = "Statistical"
    HYBRID = "Hybrid"


# ── 1. Weather ──────────────────────────────────────────────────────────────
class WeatherData(BaseModel):
    """Normalized weather conditions per solar farm (v1)."""

    farm_id: str
    timestamp: datetime
    temperature_c: float
    cloud_cover_pct: float
    irradiance_wm2: float
    wind_speed_ms: float
    precipitation_prob: float = Field(ge=0.0, le=1.0)
    uv_index: float
    source: str


# ── 2. Forecast ─────────────────────────────────────────────────────────────
class SolarForecast(BaseModel):
    """Predicted energy generation (v1)."""

    farm_id: str
    timestamp: datetime
    predicted_energy_kwh: float
    confidence_lower: float
    confidence_upper: float
    peak_generation_time: datetime
    model_version: str


# ── 3. Actual energy observation ────────────────────────────────────────────
class EnergyObservation(BaseModel):
    """Actual solar farm output (v1)."""

    farm_id: str
    timestamp: datetime
    energy_kwh: float
    inverter_status: InverterStatus
    panel_temperature_c: float
    voltage_v: float
    current_a: float


# ── 4. Anomaly ──────────────────────────────────────────────────────────────
class AnomalyDetectionResult(BaseModel):
    """Detected deviations (v1)."""

    farm_id: str
    timestamp: datetime
    anomaly_score: float = Field(ge=0.0, le=1.0)
    severity: Severity
    deviation_pct: float
    detection_method: DetectionMethod
    explanation_stub: str


# ── 5. Root cause analysis ──────────────────────────────────────────────────
class RCAResult(BaseModel):
    """LLM-generated explanation of anomalies (v1)."""

    farm_id: str
    timestamp: datetime
    root_causes: list[str]
    cause_weights: list[float]
    confidence_score: float = Field(ge=0.0, le=1.0)
    explanation_text: str
    supporting_signals: list[str]


# ── 7. Human-in-the-loop ────────────────────────────────────────────────────
class ApprovalRequest(BaseModel):
    """Approval request for a critical action (v1)."""

    request_id: str
    farm_id: str
    action_type: ActionType
    severity: Severity
    description: str
    proposed_by: str
    timestamp: datetime
    status: ApprovalStatus = ApprovalStatus.PENDING


class ApprovalDecision(BaseModel):
    """Human decision on an approval request (v1)."""

    request_id: str
    decision: ApprovalStatus
    reviewer: str
    timestamp: datetime
    notes: Optional[str] = None


# ── 8. RAG ──────────────────────────────────────────────────────────────────
class DocumentChunk(BaseModel):
    """A single retrievable chunk of a maintenance document (v1)."""

    doc_id: str
    chunk_id: str
    content: str
    embedding: Optional[list[float]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RAGQueryResult(BaseModel):
    """Result of a grounded RAG query (v1)."""

    query: str
    retrieved_chunks: list[DocumentChunk]
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)


# ── 9. Forecast evaluation ──────────────────────────────────────────────────
class ForecastEvaluation(BaseModel):
    """Forecast error metrics (v1)."""

    farm_id: str
    timestamp: datetime
    mae: float
    rmse: float
    mape: float
    bias: float


# ── 6. Central agent state (LangGraph core) ─────────────────────────────────
class SystemState(BaseModel):
    """The central shared state object used across all agents (v1).

    LangGraph nodes read and write fields on this object; it is the ONLY
    shared structure passed between agents.
    """

    farm_id: str
    timestamp: datetime
    weather: Optional[WeatherData] = None
    forecast: Optional[SolarForecast] = None
    actual: Optional[EnergyObservation] = None
    anomaly: Optional[AnomalyDetectionResult] = None
    rca: Optional[RCAResult] = None
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    report: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# ── Master registry ─────────────────────────────────────────────────────────
class FarmMetadata(BaseModel):
    """Static metadata for a registered solar farm."""

    farm_id: str
    name: str
    latitude: float
    longitude: float
    capacity_kwp: float
    panel_count: int
    timezone: str = "UTC"


__all__ = [
    "SCHEMA_VERSION",
    "Severity",
    "InverterStatus",
    "ApprovalStatus",
    "ActionType",
    "DetectionMethod",
    "WeatherData",
    "SolarForecast",
    "EnergyObservation",
    "AnomalyDetectionResult",
    "RCAResult",
    "ApprovalRequest",
    "ApprovalDecision",
    "DocumentChunk",
    "RAGQueryResult",
    "ForecastEvaluation",
    "SystemState",
    "FarmMetadata",
]
