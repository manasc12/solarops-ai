"""ML layer tests: schema-compliant forecasting and anomaly detection."""

from __future__ import annotations

from backend.app.models.schemas import AnomalyDetectionResult, Severity, SolarForecast
from backend.app.services.anomaly_service import get_anomaly_service
from backend.app.services.forecast_service import get_forecast_service


def test_forecast_is_schema_compliant_and_positive():
    forecast = get_forecast_service().generate("FARM_001", horizon_hours=24)
    assert isinstance(forecast, SolarForecast)
    assert forecast.predicted_energy_kwh > 0
    assert forecast.confidence_lower <= forecast.predicted_energy_kwh <= forecast.confidence_upper
    assert forecast.model_version == "v1"


def test_normal_farm_low_severity():
    result = get_anomaly_service().detect("FARM_001", inject_fault=False)
    assert isinstance(result, AnomalyDetectionResult)
    assert 0.0 <= result.anomaly_score <= 1.0
    assert result.severity in {Severity.LOW, Severity.MEDIUM}


def test_faulted_farm_flags_high_anomaly():
    result = get_anomaly_service().detect("FARM_002", inject_fault=True)
    assert result.anomaly_score >= 0.6
    assert result.severity == Severity.HIGH
    assert abs(result.deviation_pct) > 10
