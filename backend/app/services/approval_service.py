"""Approval service: lifecycle management for human-in-the-loop decisions.

Owns creation of approval requests, recording of decisions (with auditable
history), and status queries. The only component that mutates approval state.
"""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.core.logging import get_logger, log_event
from backend.app.db.repository import ApprovalRepository, FarmRepository
from backend.app.models.schemas import (
    ActionType,
    ApprovalDecision,
    ApprovalRequest,
    ApprovalStatus,
    Severity,
)
from backend.app.utils.helpers import new_id

logger = get_logger("services.approval")


class ApprovalService:
    def __init__(self) -> None:
        self._repo = ApprovalRepository()
        self._farms = FarmRepository()

    def submit(
        self,
        farm_id: str,
        action_type: ActionType,
        severity: Severity,
        description: str,
        proposed_by: str = "system",
    ) -> ApprovalRequest:
        if not self._farms.exists(farm_id):
            raise ValueError(f"Unknown farm_id (not in master registry): {farm_id}")
        request = ApprovalRequest(
            request_id=new_id("appr_"),
            farm_id=farm_id,
            action_type=action_type,
            severity=severity,
            description=description,
            proposed_by=proposed_by,
            timestamp=datetime.now(timezone.utc),
            status=ApprovalStatus.PENDING,
        )
        self._repo.save_request(request)
        log_event(
            logger,
            "approval_submitted",
            request_id=request.request_id,
            farm_id=farm_id,
            severity=severity.value,
        )
        return request

    def decide(
        self, request_id: str, decision: ApprovalStatus, reviewer: str, notes: str | None = None
    ) -> ApprovalRequest:
        request = self._repo.get_request(request_id)
        if request is None:
            raise ValueError(f"Unknown approval request: {request_id}")
        request.status = decision
        self._repo.save_request(request)
        self._repo.save_decision(
            ApprovalDecision(
                request_id=request_id,
                decision=decision,
                reviewer=reviewer,
                timestamp=datetime.now(timezone.utc),
                notes=notes,
            )
        )
        log_event(
            logger,
            "approval_decided",
            request_id=request_id,
            decision=decision.value,
            reviewer=reviewer,
        )
        return request

    def get(self, request_id: str) -> ApprovalRequest | None:
        return self._repo.get_request(request_id)

    def list_pending(self) -> list[ApprovalRequest]:
        return self._repo.list_pending()

    def list_all(self) -> list[ApprovalRequest]:
        return self._repo.list_requests()

    def decision_history(self, request_id: str) -> list[ApprovalDecision]:
        return self._repo.get_decisions(request_id)


_service: ApprovalService | None = None


def get_approval_service() -> ApprovalService:
    global _service
    if _service is None:
        _service = ApprovalService()
    return _service
