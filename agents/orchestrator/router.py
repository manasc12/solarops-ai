"""Conditional routing for the orchestrator.

Routing decisions are centralized here (only the orchestrator may branch). Each
function returns the name of the next node given the current state.
"""

from __future__ import annotations

from backend.app.models.schemas import Severity, SystemState
from workflows.state_definitions import RCA_TRIGGER_THRESHOLD


def route_after_anomaly(state: SystemState) -> str:
    """Trigger RCA only when the anomaly score crosses the threshold."""
    if state.anomaly is not None and state.anomaly.anomaly_score >= RCA_TRIGGER_THRESHOLD:
        return "rca"
    return "report"


def route_after_report(state: SystemState) -> str:
    """Open a HITL gate only for HIGH severity anomalies."""
    if state.anomaly is not None and state.anomaly.severity == Severity.HIGH:
        return "hitl"
    return "end"


def needs_rca(state: SystemState) -> bool:
    return route_after_anomaly(state) == "rca"


def needs_hitl(state: SystemState) -> bool:
    return route_after_report(state) == "hitl"
