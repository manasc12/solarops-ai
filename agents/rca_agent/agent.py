"""Root Cause Analysis Agent.

Single responsibility: explain *why* an anomaly occurred. Uses deterministic
heuristics to rank grounded candidate causes, then an LLM (or deterministic
fallback) to synthesize a human-readable explanation. Operates only on
``SystemState`` and only runs when an anomaly warrants it.
"""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.core.logging import get_logger, log_event
from backend.app.db.repository import RCARepository
from backend.app.models.schemas import RCAResult
from agents.rca_agent.prompt_templates import RCA_PROMPT_TEMPLATE, RCA_SYSTEM
from agents.rca_agent.reasoning import confidence_from_signals, rank_causes
from agents.shared.llm_client import get_llm_client
from agents.shared.state import SystemState, trace

logger = get_logger("agents.rca")
AGENT_ID = "rca-agent"


class RCAAgent:
    def __init__(self) -> None:
        self._llm = get_llm_client()
        self._repo = RCARepository()

    def run(self, state: SystemState) -> SystemState:
        if state.anomaly is None:
            trace(state, "rca_agent", skipped="no anomaly in state")
            return state

        causes, weights, signals = rank_causes(state.anomaly, state.weather, state.actual)
        confidence = confidence_from_signals(state.anomaly, len(signals))
        explanation = self._explain(state, causes)

        rca = RCAResult(
            farm_id=state.farm_id,
            timestamp=datetime.now(timezone.utc),
            root_causes=causes,
            cause_weights=weights,
            confidence_score=confidence,
            explanation_text=explanation,
            supporting_signals=signals,
        )
        state.rca = rca
        self._repo.save(rca)
        trace(state, "rca_agent", top_cause=causes[0], confidence=confidence)
        log_event(logger, "rca_agent_done", farm_id=state.farm_id, top_cause=causes[0])
        return state

    def _explain(self, state: SystemState, causes: list[str]) -> str:
        anomaly = state.anomaly
        weather = state.weather
        actual = state.actual
        prompt = RCA_PROMPT_TEMPLATE.format(
            farm_id=state.farm_id,
            anomaly_score=anomaly.anomaly_score if anomaly else "n/a",
            severity=anomaly.severity.value if anomaly else "n/a",
            deviation_pct=anomaly.deviation_pct if anomaly else "n/a",
            inverter_status=actual.inverter_status.value if actual else "unknown",
            cloud_cover_pct=weather.cloud_cover_pct if weather else "n/a",
            irradiance_wm2=weather.irradiance_wm2 if weather else "n/a",
            panel_temperature_c=actual.panel_temperature_c if actual else "n/a",
            causes="; ".join(causes),
        )
        fallback = self._deterministic_explanation(state, causes)
        return self._llm.generate(prompt, system=RCA_SYSTEM, fallback=fallback)

    @staticmethod
    def _deterministic_explanation(state: SystemState, causes: list[str]) -> str:
        anomaly = state.anomaly
        primary = causes[0] if causes else "an undetermined factor"
        dev = anomaly.deviation_pct if anomaly else 0.0
        sev = anomaly.severity.value if anomaly else "LOW"
        secondary = f" Contributing factor: {causes[1]}." if len(causes) > 1 else ""
        return (
            f"The {sev.lower()}-severity anomaly at farm {state.farm_id} is most "
            f"likely caused by {primary.lower()}. Actual output deviated {dev:.0f}% "
            f"from the forecast.{secondary}"
        )


def run(state: SystemState) -> SystemState:
    return RCAAgent().run(state)
