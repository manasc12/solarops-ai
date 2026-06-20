"""Human-in-the-loop approval logic (LangGraph blocking node).

Single responsibility: when an anomaly is critical, create a pending approval
request and mark the shared state as blocked on human review. This node does
NOT auto-approve; it gates execution until an operator decides.
"""

from __future__ import annotations

from backend.app.core.logging import get_logger, log_event
from backend.app.models.schemas import ApprovalStatus
from backend.app.services.approval_service import get_approval_service
from agents.hitl_agent.escalation_rules import proposed_action, requires_approval
from agents.shared.state import SystemState, trace

logger = get_logger("agents.hitl")
AGENT_ID = "hitl-agent"


class HITLAgent:
    def __init__(self) -> None:
        self._approvals = get_approval_service()

    def run(self, state: SystemState) -> SystemState:
        if not requires_approval(state.anomaly):
            state.approval_status = ApprovalStatus.APPROVED  # no gate needed
            trace(state, "hitl_agent", gated=False)
            return state

        action_type, description = proposed_action(state.anomaly)
        request = self._approvals.submit(
            farm_id=state.farm_id,
            action_type=action_type,
            severity=state.anomaly.severity,
            description=description,
            proposed_by=AGENT_ID,
        )
        state.approval_status = ApprovalStatus.PENDING
        state.metadata["approval_request_id"] = request.request_id
        trace(state, "hitl_agent", gated=True, request_id=request.request_id)
        log_event(
            logger,
            "hitl_gate_opened",
            farm_id=state.farm_id,
            request_id=request.request_id,
        )
        return state


def run(state: SystemState) -> SystemState:
    return HITLAgent().run(state)
