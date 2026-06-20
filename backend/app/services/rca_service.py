"""RCA service: API-facing wrapper around the RCA agent.

Builds a partial ``SystemState`` from the latest stored weather/forecast/anomaly/
actual for a farm and runs the RCA agent to produce a grounded explanation.
"""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.core.logging import get_logger
from backend.app.db.repository import (
    AnomalyRepository,
    ForecastRepository,
    ObservationRepository,
    RCARepository,
)
from backend.app.models.schemas import RCAResult, SystemState
from backend.app.services.anomaly_service import get_anomaly_service
from backend.app.services.weather_service import get_weather_service
from agents.rca_agent.agent import RCAAgent

logger = get_logger("services.rca")


class RCAService:
    def __init__(self) -> None:
        self._agent = RCAAgent()
        self._anomaly_repo = AnomalyRepository()
        self._forecast_repo = ForecastRepository()
        self._obs_repo = ObservationRepository()
        self._rca_repo = RCARepository()
        self._weather = get_weather_service()
        self._anomaly = get_anomaly_service()

    def analyze(self, farm_id: str) -> RCAResult:
        anomaly = self._anomaly_repo.get(farm_id) or self._anomaly.detect(farm_id)
        state = SystemState(
            farm_id=farm_id,
            timestamp=datetime.now(timezone.utc),
            weather=self._weather.get_current(farm_id),
            forecast=self._forecast_repo.get(farm_id),
            actual=self._obs_repo.get(farm_id),
            anomaly=anomaly,
        )
        self._agent.run(state)
        if state.rca is None:
            raise ValueError("RCA could not be produced (no anomaly context)")
        return state.rca

    def get_latest(self, farm_id: str) -> RCAResult | None:
        return self._rca_repo.get(farm_id)


_service: RCAService | None = None


def get_rca_service() -> RCAService:
    global _service
    if _service is None:
        _service = RCAService()
    return _service
