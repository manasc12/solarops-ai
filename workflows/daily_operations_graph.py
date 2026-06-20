"""Daily operations workflow entrypoint.

Thin module exposing the compiled daily-operations graph and a convenience
runner used by the API and CLI.

Run standalone:
    python -m workflows.daily_operations_graph FARM_001
"""

from __future__ import annotations

import sys

from agents.orchestrator.graph import build_graph, run_pipeline
from backend.app.models.schemas import SystemState


def run_daily_operations(farm_id: str) -> SystemState:
    return run_pipeline(farm_id)


# Compiled graph (may be None if LangGraph is unavailable; fallback handles it).
daily_operations_graph = build_graph()


if __name__ == "__main__":
    farm = sys.argv[1] if len(sys.argv) > 1 else "FARM_001"
    final = run_daily_operations(farm)
    print(final.report or "(no report)")
