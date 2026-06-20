"""Reusable card / badge render functions (presentation only)."""

from __future__ import annotations

import streamlit as st

from streamlit_app.utils.constants import SEVERITY_COLORS, SEVERITY_EMOJI, STATUS_COLORS
from streamlit_app.utils.formatters import fmt_kwh, fmt_pct, fmt_score, fmt_time


def severity_badge(severity: str) -> str:
    color = SEVERITY_COLORS.get(severity, "#555")
    emoji = SEVERITY_EMOJI.get(severity, "")
    return (
        f"<span style='background:{color};color:white;padding:3px 10px;"
        f"border-radius:12px;font-weight:600;'>{emoji} {severity}</span>"
    )


def status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, "#555")
    return (
        f"<span style='background:{color};color:white;padding:3px 10px;"
        f"border-radius:12px;font-weight:600;'>{status}</span>"
    )


def forecast_cards(forecast: dict | None) -> None:
    if not forecast:
        st.info("No forecast available.")
        return
    c1, c2, c3 = st.columns(3)
    c1.metric("Predicted (24h)", fmt_kwh(forecast.get("predicted_energy_kwh")))
    c2.metric(
        "Confidence band",
        f"{fmt_kwh(forecast.get('confidence_lower'))} – {fmt_kwh(forecast.get('confidence_upper'))}",
    )
    c3.metric("Peak time", fmt_time(forecast.get("peak_generation_time")))


def anomaly_cards(anomaly: dict | None) -> None:
    if not anomaly:
        st.info("No anomaly result available.")
        return
    c1, c2, c3 = st.columns(3)
    c1.metric("Anomaly score", fmt_score(anomaly.get("anomaly_score")))
    c2.markdown("**Severity**", unsafe_allow_html=True)
    c2.markdown(severity_badge(anomaly.get("severity", "LOW")), unsafe_allow_html=True)
    c3.metric("Deviation", fmt_pct(anomaly.get("deviation_pct")))
    if anomaly.get("explanation_stub"):
        st.caption(f"Detector note: {anomaly['explanation_stub']}")
