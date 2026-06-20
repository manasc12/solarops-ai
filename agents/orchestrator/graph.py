"""LangGraph orchestration for the daily operations workflow.

Defines the agent nodes and wires them into a LangGraph state machine:

    weather -> forecast -> anomaly -> (rca?) -> report -> (hitl?) -> END

The shared ``SystemState`` is the only object passed between nodes. If LangGraph
is unavailable, a deterministic sequential fallback executes the identical node
functions and routing so the pipeline always runs end-to-end.
"""

from __future__ import annotations

from typing import Any, Callable

from backend.app.core.logging import get_logger, log_event
from backend.app.models.schemas import SystemState
from backend.app.services.report_service import get_report_service
from agents.anomaly_agent.agent import run as anomaly_run
from agents.forecasting_agent.agent import run as forecast_run
from agents.hitl_agent.approval_logic import run as hitl_run
from agents.orchestrator.router import route_after_anomaly, route_after_report
from agents.orchestrator.state import SystemState as _State  # noqa: F401
from agents.rca_agent.agent import run as rca_run
from agents.shared.state import new_state, trace
from agents.weather_agent.agent import run as weather_run

logger = get_logger("orchestrator.graph")


# ── Node functions (operate on and return SystemState) ──────────────────────
def weather_node(state: SystemState) -> SystemState:
    return weather_run(state)


def forecast_node(state: SystemState) -> SystemState:
    return forecast_run(state)


def anomaly_node(state: SystemState) -> SystemState:
    return anomaly_run(state)


def rca_node(state: SystemState) -> SystemState:
    return rca_run(state)


def report_node(state: SystemState) -> SystemState:
    get_report_service().generate(state)
    trace(state, "report_node")
    return state


def hitl_node(state: SystemState) -> SystemState:
    return hitl_run(state)


# ── LangGraph construction ──────────────────────────────────────────────────
def _lg_wrap(fn: Callable[[SystemState], SystemState]) -> Callable[[SystemState], dict[str, Any]]:
    """Adapt a state->state node into a LangGraph node returning update dicts."""

    def _node(state: SystemState) -> dict[str, Any]:
        updated = fn(state)
        return updated.model_dump()

    return _node


def build_graph():
    """Build and compile the LangGraph app. Returns None if LangGraph is absent."""
    try:
        from langgraph.graph import END, START, StateGraph
    except Exception as exc:  # pragma: no cover - fallback path
        log_event(logger, "langgraph_unavailable", error=str(exc))
        return None

    builder = StateGraph(SystemState)
    builder.add_node("weather", _lg_wrap(weather_node))
    builder.add_node("forecast", _lg_wrap(forecast_node))
    builder.add_node("anomaly", _lg_wrap(anomaly_node))
    builder.add_node("rca", _lg_wrap(rca_node))
    builder.add_node("report", _lg_wrap(report_node))
    builder.add_node("hitl", _lg_wrap(hitl_node))

    builder.add_edge(START, "weather")
    builder.add_edge("weather", "forecast")
    builder.add_edge("forecast", "anomaly")
    builder.add_conditional_edges(
        "anomaly", route_after_anomaly, {"rca": "rca", "report": "report"}
    )
    builder.add_edge("rca", "report")
    builder.add_conditional_edges(
        "report", route_after_report, {"hitl": "hitl", "end": END}
    )
    builder.add_edge("hitl", END)
    return builder.compile()


# ── Sequential fallback (identical logic) ───────────────────────────────────
def _run_sequential(state: SystemState) -> SystemState:
    state = weather_node(state)
    state = forecast_node(state)
    state = anomaly_node(state)
    if route_after_anomaly(state) == "rca":
        state = rca_node(state)
    state = report_node(state)
    if route_after_report(state) == "hitl":
        state = hitl_node(state)
    return state


_compiled = None


def get_app():
    global _compiled
    if _compiled is None:
        _compiled = build_graph()
    return _compiled


def run_pipeline(farm_id: str) -> SystemState:
    """Execute the full daily operations workflow for a farm."""
    state = new_state(farm_id)
    app = get_app()
    if app is None:
        log_event(logger, "pipeline_run_sequential", farm_id=farm_id)
        return _run_sequential(state)

    log_event(logger, "pipeline_run_langgraph", farm_id=farm_id)
    result = app.invoke(state)
    # LangGraph returns the final state as a dict or model depending on version.
    if isinstance(result, SystemState):
        return result
    return SystemState.model_validate(result)
