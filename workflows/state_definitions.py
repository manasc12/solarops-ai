"""LangGraph state definitions.

The canonical ``SystemState`` IS the graph state. This module exposes it plus
orchestration constants so workflow modules import a single source of truth.
"""

from __future__ import annotations

from backend.app.models.schemas import SystemState  # noqa: F401

# anomaly_score at/above which the conditional RCA node is triggered.
RCA_TRIGGER_THRESHOLD = 0.6

__all__ = ["SystemState", "RCA_TRIGGER_THRESHOLD"]
