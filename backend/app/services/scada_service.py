"""SCADA telemetry service.

Provides current and historical SCADA-style energy observations for a farm.
Backed by the deterministic synthetic engine. A fault is injected deterministically
for farms whose id ends in an even hundred so the end-to-end pipeline reliably
exercises anomaly -> RCA -> HITL paths in demos and tests.
"""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.db.repository import FarmRepository
from backend.app.models.schemas import EnergyObservation, FarmMetadata
from backend.app.services.synthetic import (
    energy_from_weather,
    generate_energy_series,
    generate_weather_series,
)


def _default_fault(farm_id: str) -> bool:
    """Deterministic fault flag so demos surface a real anomaly (FARM_002)."""
    digits = "".join(ch for ch in farm_id if ch.isdigit())
    return bool(digits) and int(digits) % 2 == 0


class ScadaService:
    def __init__(self) -> None:
        self._farms = FarmRepository()

    def get_current(self, farm_id: str, inject_fault: bool | None = None) -> EnergyObservation:
        farm = self._require_farm(farm_id)
        if inject_fault is None:
            inject_fault = _default_fault(farm_id)
        weather = generate_weather_series(
            farm, hours=1, start=datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        )[0]
        return energy_from_weather(farm, weather, inject_fault=inject_fault)

    def get_series(self, farm_id: str, hours: int = 48) -> list[EnergyObservation]:
        farm = self._require_farm(farm_id)
        weather = generate_weather_series(farm, hours=hours)
        return generate_energy_series(farm, weather)

    def _require_farm(self, farm_id: str) -> FarmMetadata:
        farm = self._farms.get(farm_id)
        if farm is None:
            raise ValueError(f"Unknown farm_id (not in master registry): {farm_id}")
        return farm


_service: ScadaService | None = None


def get_scada_service() -> ScadaService:
    global _service
    if _service is None:
        _service = ScadaService()
    return _service
