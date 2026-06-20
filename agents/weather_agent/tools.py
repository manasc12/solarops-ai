"""Weather agent tools: deterministic operational indicators from weather.

These are pure functions converting raw weather into bounded operational
indicators used by the agent's structured insight.
"""

from __future__ import annotations

from backend.app.models.schemas import WeatherData


def cloud_impact_score(weather: WeatherData) -> float:
    """0 (clear) .. 1 (fully overcast) impact on generation."""
    return round(min(1.0, max(0.0, weather.cloud_cover_pct / 100.0)), 3)


def temperature_stress_index(weather: WeatherData) -> float:
    """0 .. 1 derating stress from panel temperature above 25C."""
    return round(min(1.0, max(0.0, (weather.temperature_c - 25.0) / 25.0)), 3)


def wind_risk_indicator(weather: WeatherData) -> str:
    if weather.wind_speed_ms >= 15:
        return "HIGH"
    if weather.wind_speed_ms >= 8:
        return "MEDIUM"
    return "LOW"


def irradiance_quality(weather: WeatherData) -> str:
    if weather.irradiance_wm2 >= 600:
        return "STRONG"
    if weather.irradiance_wm2 >= 200:
        return "MODERATE"
    return "WEAK"
