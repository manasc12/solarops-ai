"""Repositories: the only layer that talks to the data store.

Includes the master farm registry (loaded from configs/app_config.yaml) and
persistence for forecasts, anomalies, RCA results, approvals, and reports.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from backend.app.db import models as tables
from backend.app.db.session import get_store
from backend.app.models.schemas import (
    AnomalyDetectionResult,
    ApprovalDecision,
    ApprovalRequest,
    EnergyObservation,
    FarmMetadata,
    RCAResult,
    SolarForecast,
)

_CONFIG_PATH = Path("configs/app_config.yaml")


class FarmRepository:
    """Master registry of solar farms (single source of farm truth)."""

    def __init__(self) -> None:
        self._store = get_store()
        if not self._store.list(tables.FARMS):
            self._load_from_config()

    def _load_from_config(self) -> None:
        if not _CONFIG_PATH.exists():
            return
        data = yaml.safe_load(_CONFIG_PATH.read_text(encoding="utf-8")) or {}
        for entry in data.get("farms", []):
            farm = FarmMetadata(**entry)
            self._store.put(tables.FARMS, farm.farm_id, farm)

    def get(self, farm_id: str) -> FarmMetadata | None:
        return self._store.get(tables.FARMS, farm_id)

    def exists(self, farm_id: str) -> bool:
        return self.get(farm_id) is not None

    def list(self) -> list[FarmMetadata]:
        return self._store.list(tables.FARMS)


class ForecastRepository:
    def __init__(self) -> None:
        self._store = get_store()

    def save(self, forecast: SolarForecast) -> None:
        self._store.put(tables.FORECASTS, forecast.farm_id, forecast)

    def get(self, farm_id: str) -> SolarForecast | None:
        return self._store.get(tables.FORECASTS, farm_id)


class AnomalyRepository:
    def __init__(self) -> None:
        self._store = get_store()

    def save(self, anomaly: AnomalyDetectionResult) -> None:
        self._store.put(tables.ANOMALIES, anomaly.farm_id, anomaly)

    def get(self, farm_id: str) -> AnomalyDetectionResult | None:
        return self._store.get(tables.ANOMALIES, farm_id)


class ObservationRepository:
    def __init__(self) -> None:
        self._store = get_store()

    def save(self, observation: EnergyObservation) -> None:
        self._store.put(tables.OBSERVATIONS, observation.farm_id, observation)

    def get(self, farm_id: str) -> EnergyObservation | None:
        return self._store.get(tables.OBSERVATIONS, farm_id)


class RCARepository:
    def __init__(self) -> None:
        self._store = get_store()

    def save(self, rca: RCAResult) -> None:
        self._store.put(tables.RCA_RESULTS, rca.farm_id, rca)

    def get(self, farm_id: str) -> RCAResult | None:
        return self._store.get(tables.RCA_RESULTS, farm_id)


class ApprovalRepository:
    """Stores approval requests and their decision history (auditable)."""

    def __init__(self) -> None:
        self._store = get_store()

    def save_request(self, request: ApprovalRequest) -> None:
        self._store.put(tables.APPROVAL_REQUESTS, request.request_id, request)

    def get_request(self, request_id: str) -> ApprovalRequest | None:
        return self._store.get(tables.APPROVAL_REQUESTS, request_id)

    def list_requests(self) -> list[ApprovalRequest]:
        return self._store.list(tables.APPROVAL_REQUESTS)

    def list_pending(self) -> list[ApprovalRequest]:
        from backend.app.models.schemas import ApprovalStatus

        return [r for r in self.list_requests() if r.status == ApprovalStatus.PENDING]

    def save_decision(self, decision: ApprovalDecision) -> None:
        history = self._store.get(tables.APPROVAL_DECISIONS, decision.request_id) or []
        history.append(decision)
        self._store.put(tables.APPROVAL_DECISIONS, decision.request_id, history)

    def get_decisions(self, request_id: str) -> list[ApprovalDecision]:
        return self._store.get(tables.APPROVAL_DECISIONS, request_id) or []


class ReportRepository:
    def __init__(self) -> None:
        self._store = get_store()

    def save(self, farm_id: str, report: str) -> None:
        self._store.put(tables.REPORTS, farm_id, report)

    def get(self, farm_id: str) -> str | None:
        return self._store.get(tables.REPORTS, farm_id)
