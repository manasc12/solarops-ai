"""SQLAlchemy ORM models for SolarOps AI.

Maps all Pydantic schemas to SQLite tables.
"""

from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, Integer, Text, Enum
from sqlalchemy.ext.declarative import declarative_base

from backend.app.db.session import Base

# Reuse Base from session module
__all__ = ["Base", "FarmModel", "ForecastModel", "AnomalyModel", "ObservationModel", 
           "RCAModel", "ApprovalRequestModel", "ApprovalDecisionModel", "ReportModel"]


class FarmModel(Base):
    """Master registry of solar farms."""
    __tablename__ = "farms"

    farm_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity_kwp = Column(Float, nullable=False)
    panel_count = Column(Integer, nullable=False)
    timezone = Column(String, default="UTC")
    created_at = Column(DateTime, default=datetime.utcnow)


class ForecastModel(Base):
    """Predicted energy generation."""
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    farm_id = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    predicted_energy_kwh = Column(Float, nullable=False)
    confidence_lower = Column(Float, nullable=False)
    confidence_upper = Column(Float, nullable=False)
    peak_generation_time = Column(DateTime, nullable=False)
    model_version = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ObservationModel(Base):
    """Actual solar farm output."""
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    farm_id = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    energy_kwh = Column(Float, nullable=False)
    inverter_status = Column(String, nullable=False)  # OK, DEGRADED, FAILURE
    panel_temperature_c = Column(Float, nullable=False)
    voltage_v = Column(Float, nullable=False)
    current_a = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnomalyModel(Base):
    """Detected deviations from expected behavior."""
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    farm_id = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    severity = Column(String, nullable=False)  # LOW, MEDIUM, HIGH
    deviation_pct = Column(Float, nullable=False)
    detection_method = Column(String, nullable=False)  # IsolationForest, Statistical, Hybrid
    explanation_stub = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class RCAModel(Base):
    """Root cause analysis results."""
    __tablename__ = "rca_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    farm_id = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    root_causes = Column(Text, nullable=False)  # JSON string
    cause_weights = Column(Text, nullable=False)  # JSON string
    confidence_score = Column(Float, nullable=False)
    explanation_text = Column(Text, nullable=False)
    supporting_signals = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)


class ApprovalRequestModel(Base):
    """Approval requests for critical actions."""
    __tablename__ = "approval_requests"

    request_id = Column(String, primary_key=True)
    farm_id = Column(String, nullable=False)
    action_type = Column(String, nullable=False)  # WorkOrder, Alert, Shutdown
    severity = Column(String, nullable=False)  # LOW, MEDIUM, HIGH
    description = Column(Text, nullable=False)
    proposed_by = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    status = Column(String, default="PENDING")  # PENDING, APPROVED, REJECTED, MODIFIED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApprovalDecisionModel(Base):
    """Decisions on approval requests (audit trail)."""
    __tablename__ = "approval_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String, nullable=False)
    decision = Column(String, nullable=False)  # PENDING, APPROVED, REJECTED, MODIFIED
    reviewer = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ReportModel(Base):
    """Generated reports."""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    farm_id = Column(String, nullable=False)
    report_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
