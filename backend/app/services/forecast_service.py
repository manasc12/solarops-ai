"""Forecast service: business logic that turns ML predictions into the
canonical ``SolarForecast`` contract. No ML internals leak to the API layer.
"""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.core.logging import get_logger, log_event
from backend.app.db.repository import FarmRepository, ForecastRepository
from backend.app.models.schemas import FarmMetadata, SolarForecast, WeatherData
from backend.app.services.weather_service import get_weather_service
from ml.inference.forecast_pipeline import get_forecast_pipeline

logger = get_logger("services.forecast")

_CONFIDENCE_BAND = 0.15


class ForecastService:
    def __init__(self) -> None:
        self._farms = FarmRepository()
        self._weather = get_weather_service()
        self._pipeline = get_forecast_pipeline()
        self._repo = ForecastRepository()

    def generate(self, farm_id: str, horizon_hours: int = 24) -> SolarForecast:
        farm = self._require_farm(farm_id)
        weather_series = self._weather.get_series(farm_id, hours=horizon_hours)
        forecast = self._forecast_from_weather(farm, weather_series)
        self._repo.save(forecast)
        log_event(
            logger,
            "forecast_generated",
            farm_id=farm_id,
            predicted_kwh=forecast.predicted_energy_kwh,
            horizon_hours=horizon_hours,
        )
        return forecast

    def _forecast_from_weather(
        self, farm: FarmMetadata, weather_series: list[WeatherData]
    ) -> SolarForecast:
        records = [w.model_dump() for w in weather_series]
        hourly = self._pipeline.predict_series(records)

        total = round(sum(hourly), 3)
        peak_idx = max(range(len(hourly)), key=lambda i: hourly[i]) if hourly else 0
        peak_time = weather_series[peak_idx].timestamp if weather_series else datetime.now(timezone.utc)

        return SolarForecast(
            farm_id=farm.farm_id,
            timestamp=datetime.now(timezone.utc),
            predicted_energy_kwh=total,
            confidence_lower=round(total * (1 - _CONFIDENCE_BAND), 3),
            confidence_upper=round(total * (1 + _CONFIDENCE_BAND), 3),
            peak_generation_time=peak_time,
            model_version=self._pipeline.model_version,
        )

    def get_latest(self, farm_id: str) -> SolarForecast | None:
        return self._repo.get(farm_id)

    def _require_farm(self, farm_id: str) -> FarmMetadata:
        farm = self._farms.get(farm_id)
        if farm is None:
            raise ValueError(f"Unknown farm_id (not in master registry): {farm_id}")
        return farm


_service: ForecastService | None = None


def get_forecast_service() -> ForecastService:
    global _service
    if _service is None:
        _service = ForecastService()
    return _service
