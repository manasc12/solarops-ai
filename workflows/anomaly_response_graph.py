"""Anomaly response workflow.

A focused sub-flow: detect anomaly -> (RCA if needed) -> open HITL gate for HIGH
severity. Reuses the orchestrator node functions and routing.

Run standalone:
    python -m workflows.anomaly_response_graph FARM_002
"""

from __future__ import annotations

import sys

from agents.orchestrator.graph import anomaly_node, hitl_node, rca_node
from agents.orchestrator.router import route_after_anomaly, route_after_report
from agents.shared.state import new_state
from backend.app.models.schemas import SystemState


def run_anomaly_response(farm_id: str) -> SystemState:
    state = new_state(farm_id)
    state = anomaly_node(state)
    if route_after_anomaly(state) == "rca":
        state = rca_node(state)
    if route_after_report(state) == "hitl":
        state = hitl_node(state)
    return state


if __name__ == "__main__":
    farm = sys.argv[1] if len(sys.argv) > 1 else "FARM_002"
    final = run_anomaly_response(farm)
    print(f"farm={final.farm_id} severity={getattr(final.anomaly, 'severity', None)} "
          f"approval={final.approval_status.value}")
