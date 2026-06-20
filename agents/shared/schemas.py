"""Shared agent schemas.

Agents MUST use the single canonical contract definitions. This module simply
re-exports them so agent code never re-defines data structures.
"""

from __future__ import annotations

from backend.app.models.schemas import (  # noqa: F401
    AnomalyDetectionResult,
    ApprovalStatus,
    DetectionMethod,
    EnergyObservation,
    FarmMetadata,
    RCAResult,
    Severity,
    SolarForecast,
    SystemState,
    WeatherData,
)

__all__ = [
    "AnomalyDetectionResult",
    "ApprovalStatus",
    "DetectionMethod",
    "EnergyObservation",
    "FarmMetadata",
    "RCAResult",
    "Severity",
    "SolarForecast",
    "SystemState",
    "WeatherData",
]
