"""Synthetic data engine.

A deterministic, physics-lite simulator that produces coherent weather and
energy time-series for a farm. It is the shared backbone for:
  * the mock weather provider,
  * ML training data,
  * SCADA-style telemetry (actual observations).

Determinism (seeded by farm_id) keeps ML training and tests reproducible, while
small seeded noise makes the series realistic.
"""

from __future__ import annotations

import math
import random
from datetime import datetime, timedelta, timezone

from backend.app.models.schemas import (
    EnergyObservation,
    FarmMetadata,
    InverterStatus,
    WeatherData,
)


def _seed_for(farm_id: str, salt: str = "") -> int:
    return abs(hash(f"{farm_id}:{salt}")) % (2**32)


def _solar_elevation_factor(hour: float, day_of_year: int, latitude: float) -> float:
    """Return a 0..1 factor approximating solar elevation for the hour.

    Uses a simple sinusoidal day model; produces 0 at night and a midday peak
    that shifts seasonally with latitude.
    """
    # Daylight window roughly centered on solar noon (~12:00 local proxy).
    declination = 23.45 * math.sin(math.radians(360.0 * (284 + day_of_year) / 365.0))
    seasonal = math.cos(math.radians(latitude - declination)) ** 2
    day_angle = math.pi * (hour - 6.0) / 12.0  # 0 at 06:00, pi at 18:00
    if day_angle <= 0 or day_angle >= math.pi:
        return 0.0
    return max(0.0, math.sin(day_angle)) * max(0.1, seasonal)


def generate_weather_series(
    farm: FarmMetadata, hours: int = 48, start: datetime | None = None
) -> list[WeatherData]:
    """Generate an hourly weather series for a farm."""
    rng = random.Random(_seed_for(farm.farm_id, "weather"))
    start = start or datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    series: list[WeatherData] = []
    base_cloud = rng.uniform(5, 45)
    for i in range(hours):
        ts = start + timedelta(hours=i)
        doy = ts.timetuple().tm_yday
        elev = _solar_elevation_factor(ts.hour + ts.minute / 60.0, doy, farm.latitude)
        cloud = min(100.0, max(0.0, base_cloud + rng.gauss(0, 12)))
        irradiance = round(1000.0 * elev * (1.0 - 0.7 * cloud / 100.0), 2)
        temp = round(15.0 + 12.0 * elev + rng.gauss(0, 2), 2)
        series.append(
            WeatherData(
                farm_id=farm.farm_id,
                timestamp=ts,
                temperature_c=temp,
                cloud_cover_pct=round(cloud, 2),
                irradiance_wm2=irradiance,
                wind_speed_ms=round(abs(rng.gauss(3.0, 1.5)), 2),
                precipitation_prob=round(min(1.0, max(0.0, cloud / 100.0 + rng.gauss(0, 0.1))), 3),
                uv_index=round(max(0.0, 11.0 * elev * (1.0 - cloud / 150.0)), 2),
                source="mock",
            )
        )
    return series


def expected_energy_kwh(farm: FarmMetadata, weather: WeatherData) -> float:
    """Clean physics-expected generation for the observed weather (no noise/fault).

    This is the weather-adjusted baseline used by performance-ratio anomaly
    detection: a healthy farm under these conditions *should* produce roughly
    this much energy. Deterministic — depends only on farm capacity and weather.
    """
    temp_derate = 1.0 - max(0.0, (weather.temperature_c - 25.0)) * 0.004
    irradiance_factor = weather.irradiance_wm2 / 1000.0
    return round(max(0.0, farm.capacity_kwp * irradiance_factor * temp_derate), 4)


def energy_from_weather(
    farm: FarmMetadata, weather: WeatherData, *, inject_fault: bool = False, rng: random.Random | None = None
) -> EnergyObservation:
    """Map a weather sample to a SCADA-style energy observation."""
    rng = rng or random.Random(_seed_for(farm.farm_id, "energy"))
    # Temperature derating: panels lose efficiency above 25C.
    temp_derate = 1.0 - max(0.0, (weather.temperature_c - 25.0)) * 0.004
    irradiance_factor = weather.irradiance_wm2 / 1000.0
    ideal_kwh = farm.capacity_kwp * irradiance_factor * temp_derate
    noise = rng.gauss(1.0, 0.03)
    energy = max(0.0, ideal_kwh * noise)

    status = InverterStatus.OK
    if inject_fault:
        # Simulate a degraded/failed string dragging output down.
        if rng.random() < 0.5:
            status = InverterStatus.FAILURE
            energy *= rng.uniform(0.1, 0.35)
        else:
            status = InverterStatus.DEGRADED
            energy *= rng.uniform(0.45, 0.7)

    panel_temp = round(weather.temperature_c + 0.03 * weather.irradiance_wm2, 2)
    voltage = round(600.0 + rng.gauss(0, 8), 2)
    current = round((energy * 1000.0) / max(voltage, 1.0), 2)
    return EnergyObservation(
        farm_id=farm.farm_id,
        timestamp=weather.timestamp,
        energy_kwh=round(energy, 2),
        inverter_status=status,
        panel_temperature_c=panel_temp,
        voltage_v=voltage,
        current_a=current,
    )


def generate_energy_series(
    farm: FarmMetadata,
    weather_series: list[WeatherData],
    *,
    fault_hours: set[int] | None = None,
) -> list[EnergyObservation]:
    """Generate SCADA energy observations aligned to a weather series.

    ``fault_hours`` indexes (into the series) where equipment faults are injected.
    """
    rng = random.Random(_seed_for(farm.farm_id, "energy"))
    fault_hours = fault_hours or set()
    observations: list[EnergyObservation] = []
    for idx, weather in enumerate(weather_series):
        observations.append(
            energy_from_weather(farm, weather, inject_fault=idx in fault_hours, rng=rng)
        )
    return observations
