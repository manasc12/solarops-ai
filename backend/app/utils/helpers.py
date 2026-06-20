"""Generic helpers shared across the backend."""

from __future__ import annotations

import uuid
from pathlib import Path


def new_id(prefix: str = "") -> str:
    suffix = uuid.uuid4().hex[:12]
    return f"{prefix}{suffix}" if prefix else suffix


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
