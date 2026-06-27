"""Repositories: the only layer that talks to the database.

Includes the master farm registry (loaded from configs/app_config.yaml) and
persistence for forecasts, anomalies, RCA results, approvals, and reports.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from backend.app.db.models import (
    FarmModel, ForecastModel, AnomalyModel, ObservationModel,
    RCAModel, ApprovalRequestModel, ApprovalDecisionModel, ReportModel
)
from backend.app.db.session import get_session
from backend.app.models.schemas import (
    AnomalyDetectionResult, ApprovalDecision, ApprovalRequest,
    EnergyObservation, FarmMetadata, RCAResult, SolarForecast, ApprovalStatus
)

logger = logging.getLogger(__name__)
_CONFIG_PATH = Path("configs/app_config.yaml")


class FarmRepository:
    """Master registry of solar farms (single source of farm truth)."""

    def __init__(self) -> None:
        self.session: Session = get_session()
        if not self.session.query(FarmModel).first():
            self._load_from_config()

    def _load_from_config(self) -> None:
        """Load farms from app_config.yaml into database."""
        if not _CONFIG_PATH.exists():
            logger.warning(f"Config file not found: {_CONFIG_PATH}")
            return
        
        data = yaml.safe_load(_CONFIG_PATH.read_text(encoding="utf-8")) or {}
        for entry in data.get("farms", []):
            farm_schema = FarmMetadata(**entry)
            farm_model = FarmModel(
                farm_id=farm_schema.farm_id,
                name=farm_schema.name,
                latitude=farm_schema.latitude,
                longitude=farm_schema.longitude,
                capacity_kwp=farm_schema.capacity_kwp,
                panel_count=farm_schema.panel_count,
                timezone=farm_schema.timezone,
            )
            self.session.merge(farm_model)
        self.session.commit()
        logger.info(f"Loaded {len(data.get('farms', []))} farms from config")

    def get(self, farm_id: str) -> FarmMetadata | None:
        """Get farm by ID."""
        farm_model = self.session.query(FarmModel).filter(FarmModel.farm_id == farm_id).first()
        if farm_model:
            return FarmMetadata(
                farm_id=farm_model.farm_id,
                name=farm_model.name,
                latitude=farm_model.latitude,
                longitude=farm_model.longitude,
                capacity_kwp=farm_model.capacity_kwp,
                panel_count=farm_model.panel_count,
                timezone=farm_model.timezone,
            )
        return None

    def exists(self, farm_id: str) -> bool:
        """Check if farm exists."""
        return self.get(farm_id) is not None

    def list(self) -> list[FarmMetadata]:
        """List all farms."""
        farms = self.session.query(FarmModel).all()
        return [
            FarmMetadata(
                farm_id=f.farm_id,
                name=f.name,
                latitude=f.latitude,
                longitude=f.longitude,
                capacity_kwp=f.capacity_kwp,
                panel_count=f.panel_count,
                timezone=f.timezone,
            )
            for f in farms
        ]


class ForecastRepository:
    """Forecast persistence."""
    
    def __init__(self) -> None:
        self.session: Session = get_session()

    def save(self, forecast: SolarForecast) -> None:
        """Save forecast."""
        forecast_model = ForecastModel(
            farm_id=forecast.farm_id,
            timestamp=forecast.timestamp,
            predicted_energy_kwh=forecast.predicted_energy_kwh,
            confidence_lower=forecast.confidence_lower,
            confidence_upper=forecast.confidence_upper,
            peak_generation_time=forecast.peak_generation_time,
            model_version=forecast.model_version,
        )
        self.session.merge(forecast_model)
        self.session.commit()

    def get(self, farm_id: str) -> SolarForecast | None:
        """Get latest forecast for a farm."""
        forecast_model = (
            self.session.query(ForecastModel)
            .filter(ForecastModel.farm_id == farm_id)
            .order_by(ForecastModel.timestamp.desc())
            .first()
        )
        if forecast_model:
            return SolarForecast(
                farm_id=forecast_model.farm_id,
                timestamp=forecast_model.timestamp,
                predicted_energy_kwh=forecast_model.predicted_energy_kwh,
                confidence_lower=forecast_model.confidence_lower,
                confidence_upper=forecast_model.confidence_upper,
                peak_generation_time=forecast_model.peak_generation_time,
                model_version=forecast_model.model_version,
            )
        return None


class AnomalyRepository:
    """Anomaly persistence."""
    
    def __init__(self) -> None:
        self.session: Session = get_session()

    def save(self, anomaly: AnomalyDetectionResult) -> None:
        """Save anomaly."""
        anomaly_model = AnomalyModel(
            farm_id=anomaly.farm_id,
            timestamp=anomaly.timestamp,
            anomaly_score=anomaly.anomaly_score,
            severity=anomaly.severity.value,
            deviation_pct=anomaly.deviation_pct,
            detection_method=anomaly.detection_method.value,
            explanation_stub=anomaly.explanation_stub,
        )
        self.session.merge(anomaly_model)
        self.session.commit()

    def get(self, farm_id: str) -> AnomalyDetectionResult | None:
        """Get latest anomaly for a farm."""
        anomaly_model = (
            self.session.query(AnomalyModel)
            .filter(AnomalyModel.farm_id == farm_id)
            .order_by(AnomalyModel.timestamp.desc())
            .first()
        )
        if anomaly_model:
            from backend.app.models.schemas import Severity, DetectionMethod
            return AnomalyDetectionResult(
                farm_id=anomaly_model.farm_id,
                timestamp=anomaly_model.timestamp,
                anomaly_score=anomaly_model.anomaly_score,
                severity=Severity(anomaly_model.severity),
                deviation_pct=anomaly_model.deviation_pct,
                detection_method=DetectionMethod(anomaly_model.detection_method),
                explanation_stub=anomaly_model.explanation_stub,
            )
        return None


class ObservationRepository:
    """Energy observation persistence."""
    
    def __init__(self) -> None:
        self.session: Session = get_session()

    def save(self, observation: EnergyObservation) -> None:
        """Save observation."""
        observation_model = ObservationModel(
            farm_id=observation.farm_id,
            timestamp=observation.timestamp,
            energy_kwh=observation.energy_kwh,
            inverter_status=observation.inverter_status.value,
            panel_temperature_c=observation.panel_temperature_c,
            voltage_v=observation.voltage_v,
            current_a=observation.current_a,
        )
        self.session.merge(observation_model)
        self.session.commit()

    def get(self, farm_id: str) -> EnergyObservation | None:
        """Get latest observation for a farm."""
        observation_model = (
            self.session.query(ObservationModel)
            .filter(ObservationModel.farm_id == farm_id)
            .order_by(ObservationModel.timestamp.desc())
            .first()
        )
        if observation_model:
            from backend.app.models.schemas import InverterStatus
            return EnergyObservation(
                farm_id=observation_model.farm_id,
                timestamp=observation_model.timestamp,
                energy_kwh=observation_model.energy_kwh,
                inverter_status=InverterStatus(observation_model.inverter_status),
                panel_temperature_c=observation_model.panel_temperature_c,
                voltage_v=observation_model.voltage_v,
                current_a=observation_model.current_a,
            )
        return None


class RCARepository:
    """Root cause analysis result persistence."""
    
    def __init__(self) -> None:
        self.session: Session = get_session()

    def save(self, rca: RCAResult) -> None:
        """Save RCA result."""
        rca_model = RCAModel(
            farm_id=rca.farm_id,
            timestamp=rca.timestamp,
            root_causes=json.dumps(rca.root_causes),
            cause_weights=json.dumps(rca.cause_weights),
            confidence_score=rca.confidence_score,
            explanation_text=rca.explanation_text,
            supporting_signals=json.dumps(rca.supporting_signals),
        )
        self.session.merge(rca_model)
        self.session.commit()

    def get(self, farm_id: str) -> RCAResult | None:
        """Get latest RCA result for a farm."""
        rca_model = (
            self.session.query(RCAModel)
            .filter(RCAModel.farm_id == farm_id)
            .order_by(RCAModel.timestamp.desc())
            .first()
        )
        if rca_model:
            return RCAResult(
                farm_id=rca_model.farm_id,
                timestamp=rca_model.timestamp,
                root_causes=json.loads(rca_model.root_causes),
                cause_weights=json.loads(rca_model.cause_weights),
                confidence_score=rca_model.confidence_score,
                explanation_text=rca_model.explanation_text,
                supporting_signals=json.loads(rca_model.supporting_signals),
            )
        return None


class ApprovalRepository:
    """Approval requests and decision history (auditable)."""
    
    def __init__(self) -> None:
        self.session: Session = get_session()

    def save_request(self, request: ApprovalRequest) -> None:
        """Save approval request."""
        request_model = ApprovalRequestModel(
            request_id=request.request_id,
            farm_id=request.farm_id,
            action_type=request.action_type.value,
            severity=request.severity.value,
            description=request.description,
            proposed_by=request.proposed_by,
            timestamp=request.timestamp,
            status=request.status.value,
        )
        self.session.merge(request_model)
        self.session.commit()

    def get_request(self, request_id: str) -> ApprovalRequest | None:
        """Get approval request by ID."""
        request_model = (
            self.session.query(ApprovalRequestModel)
            .filter(ApprovalRequestModel.request_id == request_id)
            .first()
        )
        if request_model:
            from backend.app.models.schemas import ActionType, Severity
            return ApprovalRequest(
                request_id=request_model.request_id,
                farm_id=request_model.farm_id,
                action_type=ActionType(request_model.action_type),
                severity=Severity(request_model.severity),
                description=request_model.description,
                proposed_by=request_model.proposed_by,
                timestamp=request_model.timestamp,
                status=ApprovalStatus(request_model.status),
            )
        return None

    def list_requests(self) -> list[ApprovalRequest]:
        """List all approval requests."""
        from backend.app.models.schemas import ActionType, Severity
        request_models = self.session.query(ApprovalRequestModel).all()
        return [
            ApprovalRequest(
                request_id=rm.request_id,
                farm_id=rm.farm_id,
                action_type=ActionType(rm.action_type),
                severity=Severity(rm.severity),
                description=rm.description,
                proposed_by=rm.proposed_by,
                timestamp=rm.timestamp,
                status=ApprovalStatus(rm.status),
            )
            for rm in request_models
        ]

    def list_pending(self) -> list[ApprovalRequest]:
        """List pending approval requests."""
        return [r for r in self.list_requests() if r.status == ApprovalStatus.PENDING]

    def save_decision(self, decision: ApprovalDecision) -> None:
        """Save approval decision."""
        decision_model = ApprovalDecisionModel(
            request_id=decision.request_id,
            decision=decision.decision.value,
            reviewer=decision.reviewer,
            timestamp=decision.timestamp,
            notes=decision.notes,
        )
        self.session.add(decision_model)
        self.session.commit()
        
        # Update request status
        request_model = (
            self.session.query(ApprovalRequestModel)
            .filter(ApprovalRequestModel.request_id == decision.request_id)
            .first()
        )
        if request_model:
            request_model.status = decision.decision.value
            self.session.commit()

    def get_decisions(self, request_id: str) -> list[ApprovalDecision]:
        """Get all decisions for an approval request."""
        from backend.app.models.schemas import ApprovalStatus
        decision_models = (
            self.session.query(ApprovalDecisionModel)
            .filter(ApprovalDecisionModel.request_id == request_id)
            .order_by(ApprovalDecisionModel.timestamp)
            .all()
        )
        return [
            ApprovalDecision(
                request_id=dm.request_id,
                decision=ApprovalStatus(dm.decision),
                reviewer=dm.reviewer,
                timestamp=dm.timestamp,
                notes=dm.notes,
            )
            for dm in decision_models
        ]


class ReportRepository:
    """Report persistence."""
    
    def __init__(self) -> None:
        self.session: Session = get_session()

    def save(self, farm_id: str, report: str) -> None:
        """Save report."""
        report_model = ReportModel(farm_id=farm_id, report_content=report)
        self.session.add(report_model)
        self.session.commit()

    def get(self, farm_id: str) -> str | None:
        """Get latest report for a farm."""
        report_model = (
            self.session.query(ReportModel)
            .filter(ReportModel.farm_id == farm_id)
            .order_by(ReportModel.created_at.desc())
            .first()
        )
        return report_model.report_content if report_model else None

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
