"""Pure presentation formatters (no business logic)."""

from __future__ import annotations

from datetime import datetime


def fmt_kwh(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:,.0f} kWh"


def fmt_pct(value: float | None, decimals: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value:.{decimals}f}%"


def fmt_score(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:.2f}"


def fmt_time(value: str | None) -> str:
    if not value:
        return "—"
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M UTC")
    except ValueError:
        return value
