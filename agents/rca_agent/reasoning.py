"""Deterministic RCA reasoning heuristics.

Produces a ranked, weighted list of candidate root causes from structured
signals (anomaly, weather, actual telemetry) BEFORE any LLM synthesis. This
keeps explanations grounded and auditable; the LLM only narrates these causes.
"""

from __future__ import annotations

from backend.app.models.schemas import (
    AnomalyDetectionResult,
    EnergyObservation,
    InverterStatus,
    WeatherData,
)


def rank_causes(
    anomaly: AnomalyDetectionResult,
    weather: WeatherData | None,
    actual: EnergyObservation | None,
) -> tuple[list[str], list[float], list[str]]:
    """Return (root_causes, cause_weights, supporting_signals)."""
    candidates: list[tuple[str, float]] = []
    signals: list[str] = [
        f"anomaly_score={anomaly.anomaly_score}",
        f"deviation_pct={anomaly.deviation_pct}",
    ]

    status = actual.inverter_status if actual else None
    if status == InverterStatus.FAILURE:
        candidates.append(("Inverter hardware failure causing string outage", 0.9))
        signals.append("inverter_status=FAILURE")
    elif status == InverterStatus.DEGRADED:
        candidates.append(("Inverter degradation / partial string underperformance", 0.7))
        signals.append("inverter_status=DEGRADED")

    if weather is not None:
        if weather.cloud_cover_pct >= 70:
            candidates.append(("Reduced irradiance from heavy cloud cover", 0.6))
            signals.append(f"cloud_cover_pct={weather.cloud_cover_pct}")
        if weather.temperature_c >= 35:
            candidates.append(("Thermal derating from high panel temperature", 0.4))
            signals.append(f"temperature_c={weather.temperature_c}")

    # If a large deviation is unexplained by status/weather, suspect soiling/shading.
    if anomaly.deviation_pct >= 15 and not candidates:
        candidates.append(("Panel soiling or partial shading reducing output", 0.55))
        candidates.append(("Possible sensor or telemetry fault", 0.35))
        signals.append("unexplained_large_deviation")

    if not candidates:
        candidates.append(("No clear fault; minor stochastic variation", 0.3))

    # Sort by weight desc and normalize weights to sum to 1.
    candidates.sort(key=lambda c: c[1], reverse=True)
    total = sum(w for _, w in candidates) or 1.0
    causes = [c for c, _ in candidates]
    weights = [round(w / total, 3) for _, w in candidates]
    return causes, weights, signals


def confidence_from_signals(anomaly: AnomalyDetectionResult, n_signals: int) -> float:
    """Confidence grows with anomaly strength and amount of corroborating evidence."""
    base = 0.4 + 0.4 * min(1.0, anomaly.anomaly_score)
    bonus = min(0.2, 0.05 * n_signals)
    return round(min(1.0, base + bonus), 3)
