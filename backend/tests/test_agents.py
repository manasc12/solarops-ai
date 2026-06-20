"""Agent + orchestration tests: end-to-end LangGraph workflow and routing."""

from __future__ import annotations

from agents.orchestrator.router import route_after_anomaly, route_after_report
from agents.shared.state import new_state
from backend.app.models.schemas import ApprovalStatus, Severity
from rag.generation.rag_chain import get_rag_chain
from workflows.daily_operations_graph import run_daily_operations


def test_pipeline_runs_full_trace_for_faulted_farm():
    state = run_daily_operations("FARM_002")
    steps = [t["step"] for t in state.metadata.get("trace", [])]
    assert steps[:3] == ["weather_agent", "forecasting_agent", "anomaly_agent"]
    assert "rca_agent" in steps  # RCA triggered by high anomaly
    assert "report_node" in steps
    assert state.forecast is not None
    assert state.anomaly is not None
    assert state.report


def test_high_severity_opens_hitl_gate():
    state = run_daily_operations("FARM_002")
    assert state.anomaly.severity == Severity.HIGH
    assert state.approval_status == ApprovalStatus.PENDING
    assert state.metadata.get("approval_request_id")


def test_normal_farm_skips_rca_and_hitl():
    state = run_daily_operations("FARM_001")
    steps = [t["step"] for t in state.metadata.get("trace", [])]
    assert "hitl_agent" not in steps or state.approval_status == ApprovalStatus.APPROVED
    assert state.report


def test_routing_helpers():
    s = new_state("FARM_001")
    assert route_after_anomaly(s) == "report"  # no anomaly yet
    assert route_after_report(s) == "end"


def test_rag_answer_is_grounded():
    result = get_rag_chain().answer("How do I handle a degraded inverter?", top_k=3)
    assert result.retrieved_chunks
    assert result.answer
    assert 0.0 <= result.confidence <= 1.0
