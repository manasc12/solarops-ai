"""Report service: composes the daily solar operations summary from state.

Pure presentation/composition of already-structured results. Uses the LLM only
to polish narrative summary text (with a deterministic fallback).
"""

from __future__ import annotations

from backend.app.core.logging import get_logger, log_event
from backend.app.db.repository import ReportRepository
from backend.app.models.schemas import SystemState
from agents.shared.llm_client import get_llm_client

logger = get_logger("services.report")

_REPORT_SYSTEM = "You are a solar operations analyst writing a concise daily shift report."


class ReportService:
    def __init__(self) -> None:
        self._llm = get_llm_client()
        self._repo = ReportRepository()

    def generate(self, state: SystemState) -> str:
        report = self._compose(state)
        narrative = self._llm.generate(
            self._narrative_prompt(state), system=_REPORT_SYSTEM, fallback=self._headline(state)
        )
        full = f"{narrative}\n\n{report}"
        state.report = full
        self._repo.save(state.farm_id, full)
        log_event(logger, "report_generated", farm_id=state.farm_id)
        return full

    def _compose(self, state: SystemState) -> str:
        lines: list[str] = [f"# Daily Operations Report — {state.farm_id}", ""]
        lines.append(f"Generated: {state.timestamp.isoformat()}")
        lines.append("")

        lines.append("## Production Forecast")
        if state.forecast:
            f = state.forecast
            lines.append(
                f"- Predicted: {f.predicted_energy_kwh:.0f} kWh "
                f"(band {f.confidence_lower:.0f}–{f.confidence_upper:.0f} kWh)"
            )
            lines.append(f"- Peak generation: {f.peak_generation_time.isoformat()}")
            lines.append(f"- Model: {f.model_version}")
        else:
            lines.append("- No forecast available")
        lines.append("")

        lines.append("## Risk & Anomalies")
        if state.anomaly:
            a = state.anomaly
            lines.append(
                f"- Anomaly score: {a.anomaly_score:.2f} | Severity: {a.severity.value}"
            )
            lines.append(f"- Forecast vs actual deviation: {a.deviation_pct:.1f}%")
            lines.append(f"- Detection: {a.detection_method.value} — {a.explanation_stub}")
        else:
            lines.append("- No anomalies detected")
        lines.append("")

        lines.append("## Root Cause Analysis")
        if state.rca:
            r = state.rca
            lines.append(f"- {r.explanation_text}")
            lines.append("- Ranked causes:")
            for cause, weight in zip(r.root_causes, r.cause_weights):
                lines.append(f"  - {cause} ({weight:.0%})")
            lines.append(f"- Confidence: {r.confidence_score:.0%}")
        else:
            lines.append("- RCA not required")
        lines.append("")

        lines.append("## Recommendations")
        lines.extend(f"- {rec}" for rec in self._recommendations(state))
        lines.append("")

        lines.append("## Governance")
        lines.append(f"- Approval status: {state.approval_status.value}")
        if state.metadata.get("approval_request_id"):
            lines.append(f"- Pending approval request: {state.metadata['approval_request_id']}")
        return "\n".join(lines)

    @staticmethod
    def _recommendations(state: SystemState) -> list[str]:
        recs: list[str] = []
        if state.anomaly and state.anomaly.severity.value == "HIGH":
            recs.append("Dispatch field inspection; await operator approval before work order.")
        elif state.anomaly and state.anomaly.severity.value == "MEDIUM":
            recs.append("Schedule diagnostic review within 24h.")
        else:
            recs.append("Continue normal monitoring.")
        if state.weather and state.weather.cloud_cover_pct >= 70:
            recs.append("Expect reduced output due to cloud cover; adjust dispatch plan.")
        return recs

    def _headline(self, state: SystemState) -> str:
        sev = state.anomaly.severity.value if state.anomaly else "NONE"
        kwh = state.forecast.predicted_energy_kwh if state.forecast else 0.0
        return (
            f"Farm {state.farm_id}: forecast {kwh:.0f} kWh next 24h; "
            f"anomaly risk {sev}."
        )

    def _narrative_prompt(self, state: SystemState) -> str:
        return (
            f"Write a 2-sentence shift summary. Farm {state.farm_id}. "
            f"Forecast {getattr(state.forecast, 'predicted_energy_kwh', 'n/a')} kWh. "
            f"Anomaly severity {getattr(state.anomaly, 'severity', 'NONE')}. "
            f"RCA: {getattr(state.rca, 'explanation_text', 'none')}."
        )


_service: ReportService | None = None


def get_report_service() -> ReportService:
    global _service
    if _service is None:
        _service = ReportService()
    return _service
