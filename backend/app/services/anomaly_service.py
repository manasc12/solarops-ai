"""Anomaly service: compares forecast vs actual output and classifies severity.

Produces the canonical ``AnomalyDetectionResult``. ML scoring is delegated to
the anomaly inference pipeline; this service owns the business rules (severity
bands, deviation, preliminary non-LLM explanation stub).
"""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.core.logging import get_logger, log_event
from backend.app.db.repository import AnomalyRepository, FarmRepository, ObservationRepository
from backend.app.models.schemas import (
    AnomalyDetectionResult,
    DetectionMethod,
    EnergyObservation,
    FarmMetadata,
    InverterStatus,
    Severity,
    WeatherData,
)
from backend.app.services.scada_service import _default_fault, get_scada_service
from backend.app.services.synthetic import energy_from_weather, expected_energy_kwh
from backend.app.services.weather_service import get_weather_service
from ml.features.anomaly_features import build_anomaly_vector, deviation_pct
from ml.inference.anomaly_pipeline import get_anomaly_pipeline

logger = get_logger("services.anomaly")

_SEVERITY_MEDIUM = 0.6
_SEVERITY_HIGH = 0.8


class AnomalyService:
    def __init__(self) -> None:
        self._farms = FarmRepository()
        self._weather = get_weather_service()
        self._scada = get_scada_service()
        self._detector = get_anomaly_pipeline()
        self._repo = AnomalyRepository()
        self._obs_repo = ObservationRepository()

    def detect(self, farm_id: str, inject_fault: bool | None = None) -> AnomalyDetectionResult:
        farm = self._require_farm(farm_id)
        # Performance-ratio detection: compare actual SCADA output against the
        # weather-expected (physics) baseline. We evaluate at the deterministic
        # peak-generation hour so the fault signal is visible (at night both
        # expected and actual are ~0) and detection is wall-clock independent.
        weather_series = self._weather.get_series(farm_id, hours=24)
        peak_idx = max(
            range(len(weather_series)),
            key=lambda i: weather_series[i].irradiance_wm2,
        )
        weather = weather_series[peak_idx]
        predicted = expected_energy_kwh(farm, weather)

        if inject_fault is None:
            inject_fault = _default_fault(farm_id)
        actual = energy_from_weather(farm, weather, inject_fault=inject_fault)

        vector = build_anomaly_vector(predicted, actual, weather, farm.capacity_kwp)
        score = self._detector.score(vector)
        dev = deviation_pct(predicted, actual.energy_kwh)
        severity = self._severity(score)

        result = AnomalyDetectionResult(
            farm_id=farm_id,
            timestamp=datetime.now(timezone.utc),
            anomaly_score=score,
            severity=severity,
            deviation_pct=round(dev, 3),
            detection_method=DetectionMethod.ISOLATION_FOREST,
            explanation_stub=self._stub(actual, dev, weather),
        )
        self._repo.save(result)
        self._obs_repo.save(actual)
        log_event(
            logger,
            "anomaly_detected",
            farm_id=farm_id,
            anomaly_score=score,
            severity=severity.value,
            deviation_pct=result.deviation_pct,
        )
        return result

    @staticmethod
    def _severity(score: float) -> Severity:
        if score >= _SEVERITY_HIGH:
            return Severity.HIGH
        if score >= _SEVERITY_MEDIUM:
            return Severity.MEDIUM
        return Severity.LOW

    @staticmethod
    def _stub(actual: EnergyObservation, dev: float, weather: WeatherData) -> str:
        reasons: list[str] = []
        if actual.inverter_status == InverterStatus.FAILURE:
            reasons.append("inverter failure reported")
        elif actual.inverter_status == InverterStatus.DEGRADED:
            reasons.append("inverter operating in degraded mode")
        if dev > 20:
            reasons.append(f"actual output {dev:.0f}% below forecast")
        if weather.cloud_cover_pct > 70:
            reasons.append("heavy cloud cover")
        return "; ".join(reasons) if reasons else "no significant deviation detected"

    def get_latest(self, farm_id: str) -> AnomalyDetectionResult | None:
        return self._repo.get(farm_id)

    def _require_farm(self, farm_id: str) -> FarmMetadata:
        farm = self._farms.get(farm_id)
        if farm is None:
            raise ValueError(f"Unknown farm_id (not in master registry): {farm_id}")
        return farm


_service: AnomalyService | None = None


def get_anomaly_service() -> AnomalyService:
    global _service
    if _service is None:
        _service = AnomalyService()
    return _service
