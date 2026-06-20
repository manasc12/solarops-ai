"""Central agent state helpers built on the canonical ``SystemState``."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.models.schemas import ApprovalStatus, SystemState


def new_state(farm_id: str) -> SystemState:
    """Create a fresh execution state for a farm."""
    return SystemState(
        farm_id=farm_id,
        timestamp=datetime.now(timezone.utc),
        approval_status=ApprovalStatus.PENDING,
        metadata={"trace": []},
    )


def trace(state: SystemState, step: str, **info: object) -> None:
    """Append an auditable execution step to the state's metadata trace."""
    entry = {"step": step, "ts": datetime.now(timezone.utc).isoformat(), **info}
    state.metadata.setdefault("trace", []).append(entry)


__all__ = ["SystemState", "new_state", "trace"]
