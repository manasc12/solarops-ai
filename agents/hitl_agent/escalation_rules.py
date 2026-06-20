"""Escalation rules: decide when human approval is mandatory.

A critical action requires human approval if it is HIGH severity, or triggers an
external action (work order, alert, shutdown), or affects production systems.
"""

from __future__ import annotations

from backend.app.models.schemas import ActionType, AnomalyDetectionResult, Severity


def requires_approval(anomaly: AnomalyDetectionResult | None) -> bool:
    """True when the anomaly warrants a gated, human-approved action."""
    if anomaly is None:
        return False
    return anomaly.severity == Severity.HIGH


def proposed_action(anomaly: AnomalyDetectionResult) -> tuple[ActionType, str]:
    """Map an anomaly to a proposed external action and description."""
    if anomaly.severity == Severity.HIGH:
        return (
            ActionType.WORK_ORDER,
            f"Dispatch field maintenance work order for farm {anomaly.farm_id}: "
            f"{anomaly.explanation_stub} (deviation {anomaly.deviation_pct:.0f}%).",
        )
    return (
        ActionType.ALERT,
        f"Raise monitoring alert for farm {anomaly.farm_id}: {anomaly.explanation_stub}.",
    )
