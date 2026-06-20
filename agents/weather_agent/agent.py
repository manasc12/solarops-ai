"""Weather Intelligence Agent.

Single responsibility: enrich the shared state with normalized weather and
bounded operational indicators. Operates only on ``SystemState``; never calls
other agents.
"""

from __future__ import annotations

from backend.app.core.logging import get_logger, log_event
from backend.app.services.weather_service import get_weather_service
from agents.shared.state import SystemState, trace
from agents.weather_agent.tools import (
    cloud_impact_score,
    irradiance_quality,
    temperature_stress_index,
    wind_risk_indicator,
)

logger = get_logger("agents.weather")
AGENT_ID = "weather-agent"


class WeatherAgent:
    def __init__(self) -> None:
        self._weather = get_weather_service()

    def run(self, state: SystemState) -> SystemState:
        weather = self._weather.get_current(state.farm_id)
        state.weather = weather
        insights = {
            "cloud_impact": cloud_impact_score(weather),
            "temp_stress": temperature_stress_index(weather),
            "wind_risk": wind_risk_indicator(weather),
            "irradiance_quality": irradiance_quality(weather),
        }
        state.metadata["weather_insights"] = insights
        trace(state, "weather_agent", **insights)
        log_event(logger, "weather_agent_done", farm_id=state.farm_id, **insights)
        return state


def run(state: SystemState) -> SystemState:
    return WeatherAgent().run(state)
