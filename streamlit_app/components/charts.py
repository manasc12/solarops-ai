"""Reusable Plotly chart render functions (presentation only)."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st


def forecast_band_chart(forecast: dict | None) -> None:
    if not forecast:
        return
    point = forecast.get("predicted_energy_kwh", 0.0)
    lower = forecast.get("confidence_lower", point)
    upper = forecast.get("confidence_upper", point)
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=["Forecast (24h)"],
            y=[point],
            name="Predicted",
            marker_color="#1565c0",
            error_y=dict(
                type="data",
                symmetric=False,
                array=[upper - point],
                arrayminus=[point - lower],
            ),
        )
    )
    fig.update_layout(height=320, yaxis_title="Energy (kWh)", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def anomaly_gauge(anomaly: dict | None) -> None:
    if not anomaly:
        return
    score = anomaly.get("anomaly_score", 0.0)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Anomaly score"},
            gauge={
                "axis": {"range": [0, 1]},
                "bar": {"color": "#37474f"},
                "steps": [
                    {"range": [0, 0.6], "color": "#a5d6a7"},
                    {"range": [0.6, 0.8], "color": "#fff59d"},
                    {"range": [0.8, 1.0], "color": "#ef9a9a"},
                ],
            },
        )
    )
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True)


def cause_weights_chart(rca: dict | None) -> None:
    if not rca or not rca.get("root_causes"):
        return
    causes = rca["root_causes"]
    weights = rca.get("cause_weights", [])
    fig = go.Figure(go.Bar(x=weights, y=causes, orientation="h", marker_color="#6a1b9a"))
    fig.update_layout(
        height=max(220, 60 * len(causes)),
        xaxis_title="Contribution",
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)
