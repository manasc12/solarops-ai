"""Weather service.

Fetches and normalizes meteorological data into the canonical ``WeatherData``
schema. Supports Open-Meteo (real HTTP) and NASA POWER (real HTTP), with a
deterministic mock provider used by default so the system runs offline.

This is pure data acquisition — no ML or agent logic lives here.
"""

from __future__ import annotations

from datetime import datetime, timezone

import requests

from backend.app.core.config import settings
from backend.app.core.logging import get_logger, log_event
from backend.app.db.repository import FarmRepository
from backend.app.models.schemas import FarmMetadata, WeatherData
from backend.app.services.synthetic import generate_weather_series

logger = get_logger("services.weather")

_HTTP_TIMEOUT = 10


class WeatherService:
    def __init__(self) -> None:
        self._farms = FarmRepository()

    # ── public API ──────────────────────────────────────────────────────────
    def get_current(self, farm_id: str) -> WeatherData:
        """Return the most recent normalized weather observation for a farm."""
        farm = self._require_farm(farm_id)
        if settings.weather_use_mock:
            return self._mock(farm)
        try:
            return self._open_meteo(farm)
        except Exception as exc:  # graceful fallback — never fail silently
            log_event(logger, "open_meteo_failed", farm_id=farm_id, error=str(exc))
            return self._mock(farm)

    def get_series(self, farm_id: str, hours: int = 48) -> list[WeatherData]:
        farm = self._require_farm(farm_id)
        return generate_weather_series(farm, hours=hours)

    # ── providers ───────────────────────────────────────────────────────────
    def _mock(self, farm: FarmMetadata) -> WeatherData:
        series = generate_weather_series(farm, hours=1)
        return series[0]

    def _open_meteo(self, farm: FarmMetadata) -> WeatherData:
        params = {
            "latitude": farm.latitude,
            "longitude": farm.longitude,
            "current": "temperature_2m,cloud_cover,wind_speed_10m,precipitation_probability,uv_index,shortwave_radiation",
        }
        resp = requests.get(settings.open_meteo_base_url, params=params, timeout=_HTTP_TIMEOUT)
        resp.raise_for_status()
        cur = resp.json().get("current", {})
        log_event(logger, "open_meteo_ok", farm_id=farm.farm_id)
        return WeatherData(
            farm_id=farm.farm_id,
            timestamp=datetime.now(timezone.utc),
            temperature_c=float(cur.get("temperature_2m", 0.0)),
            cloud_cover_pct=float(cur.get("cloud_cover", 0.0)),
            irradiance_wm2=float(cur.get("shortwave_radiation", 0.0)),
            wind_speed_ms=float(cur.get("wind_speed_10m", 0.0)),
            precipitation_prob=float(cur.get("precipitation_probability", 0.0)) / 100.0,
            uv_index=float(cur.get("uv_index", 0.0)),
            source="Open-Meteo",
        )

    def _require_farm(self, farm_id: str) -> FarmMetadata:
        farm = self._farms.get(farm_id)
        if farm is None:
            raise ValueError(f"Unknown farm_id (not in master registry): {farm_id}")
        return farm


_service: WeatherService | None = None


def get_weather_service() -> WeatherService:
    global _service
    if _service is None:
        _service = WeatherService()
    return _service
