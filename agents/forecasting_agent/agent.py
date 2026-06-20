"""Forecasting Agent.

Single responsibility: attach an ML solar forecast to the shared state and a
short reasoning note about expected production. Operates only on ``SystemState``.
"""

from __future__ import annotations

from backend.app.core.logging import get_logger, log_event
from backend.app.services.forecast_service import get_forecast_service
from agents.shared.state import SystemState, trace

logger = get_logger("agents.forecast")
AGENT_ID = "forecasting-agent"


class ForecastAgent:
    def __init__(self) -> None:
        self._forecast = get_forecast_service()

    def run(self, state: SystemState) -> SystemState:
        forecast = self._forecast.generate(state.farm_id, horizon_hours=24)
        state.forecast = forecast
        note = (
            f"Expected ~{forecast.predicted_energy_kwh:.0f} kWh over 24h "
            f"(band {forecast.confidence_lower:.0f}-{forecast.confidence_upper:.0f})."
        )
        state.metadata["forecast_note"] = note
        trace(state, "forecasting_agent", predicted_kwh=forecast.predicted_energy_kwh)
        log_event(
            logger,
            "forecast_agent_done",
            farm_id=state.farm_id,
            predicted_kwh=forecast.predicted_energy_kwh,
        )
        return state


def run(state: SystemState) -> SystemState:
    return ForecastAgent().run(state)
