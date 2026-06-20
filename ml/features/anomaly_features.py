"""Anomaly feature engineering: turn (forecast, actual, weather) into a vector.

Reusable at training (normal-behaviour fitting) and inference time so the
IsolationForest sees identical features in both paths.
"""

from __future__ import annotations

from backend.app.models.schemas import EnergyObservation, InverterStatus, WeatherData

ANOMALY_FEATURES = [
    "deviation_signed",
    "abs_deviation",
    "inverter_code",
]

_STATUS_CODE = {
    InverterStatus.OK: 0.0,
    InverterStatus.DEGRADED: 1.0,
    InverterStatus.FAILURE: 2.0,
}


def deviation_pct(predicted_kwh: float, actual_kwh: float) -> float:
    """Signed deviation of actual vs predicted as a percentage of predicted."""
    if abs(predicted_kwh) < 1e-6:
        return 0.0
    return (predicted_kwh - actual_kwh) / predicted_kwh * 100.0


def build_anomaly_vector(
    predicted_kwh: float,
    actual: EnergyObservation,
    weather: WeatherData,
    capacity_kwp: float,
) -> list[float]:
    """Scale-invariant anomaly vector.

    Detection is driven by *relative* performance deviation and inverter health,
    not by absolute production level. This keeps the normal manifold consistent
    across farms of different capacity and across the day, so a healthy farm is
    never flagged simply for producing a lot of energy at solar noon.
    """
    dev = deviation_pct(predicted_kwh, actual.energy_kwh)
    return [
        dev / 100.0,
        abs(dev) / 100.0,
        _STATUS_CODE.get(actual.inverter_status, 0.0),
    ]
