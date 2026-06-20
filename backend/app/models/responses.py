"""Global API response envelope (data_schema.md §10).

Every endpoint returns this structure:
    { "status", "data", "error", "timestamp" }
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ErrorDetail(BaseModel):
    code: str = ""
    message: str = ""


class APIResponse(BaseModel):
    """Standard envelope for all API responses."""

    status: str = "success"
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None
    timestamp: str = Field(default_factory=_now_iso)

    @classmethod
    def ok(cls, data: Any = None) -> "APIResponse":
        return cls(status="success", data=data, error=None)

    @classmethod
    def fail(cls, code: str, message: str) -> "APIResponse":
        return cls(status="error", data=None, error=ErrorDetail(code=code, message=message))
