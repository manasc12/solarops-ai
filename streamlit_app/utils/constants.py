"""Frontend presentation constants."""

from __future__ import annotations

APP_TITLE = "SolarOps AI — Solar Operations Control Center"

SEVERITY_COLORS = {
    "LOW": "#2e7d32",
    "MEDIUM": "#f9a825",
    "HIGH": "#c62828",
}

STATUS_COLORS = {
    "PENDING": "#f9a825",
    "APPROVED": "#2e7d32",
    "REJECTED": "#c62828",
    "MODIFIED": "#1565c0",
}

SEVERITY_EMOJI = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
