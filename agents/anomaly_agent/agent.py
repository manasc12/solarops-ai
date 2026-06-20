"""Anomaly Detection Agent.

Single responsibility: compare forecast vs actual output, attach a structured
anomaly result to the shared state, and flag whether downstream RCA is needed.
Operates only on ``SystemState``.
"""

from __future__ import annotations

from backend.app.core.logging import get_logger, log_event
from backend.app.db.repository import ObservationRepository
from backend.app.services.anomaly_service import get_anomaly_service
from agents.shared.state import SystemState, trace

logger = get_logger("agents.anomaly")
AGENT_ID = "anomaly-agent"


class AnomalyAgent:
    def __init__(self) -> None:
        self._anomaly = get_anomaly_service()
        self._obs_repo = ObservationRepository()

    def run(self, state: SystemState) -> SystemState:
        result = self._anomaly.detect(state.farm_id)
        state.anomaly = result
        state.actual = self._obs_repo.get(state.farm_id)
        state.metadata["anomaly_summary"] = {
            "score": result.anomaly_score,
            "severity": result.severity.value,
            "deviation_pct": result.deviation_pct,
        }
        trace(
            state,
            "anomaly_agent",
            score=result.anomaly_score,
            severity=result.severity.value,
        )
        log_event(
            logger,
            "anomaly_agent_done",
            farm_id=state.farm_id,
            score=result.anomaly_score,
            severity=result.severity.value,
        )
        return state


def run(state: SystemState) -> SystemState:
    return AnomalyAgent().run(state)
