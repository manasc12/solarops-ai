"""SolarOps AI — Streamlit entrypoint (home / overview).

Presentation only: layout, interaction handling, and rendering. All data comes
from the backend via the centralized API client. No business, ML, or agent logic.

Run:
    streamlit run streamlit_app/app.py
"""

from __future__ import annotations

import streamlit as st

from streamlit_app.components.layout import backend_status, page_header
from streamlit_app.services.api_client import APIError, get_client

page_header("Agentic Renewable Energy Operations — control center overview")
online = backend_status()

st.markdown(
    """
SolarOps AI coordinates ML forecasting, anomaly detection, LLM-based root cause
analysis, retrieval-augmented maintenance knowledge, and human-in-the-loop
governance through a LangGraph orchestrator.

Use the pages in the sidebar:
- **Dashboard** — run the full daily-operations workflow per farm
- **Forecasts** — solar production forecasts
- **Anomalies** — deviation detection and severity
- **RCA Explanations** — root-cause reasoning
- **Approvals** — human-in-the-loop action queue
- **RAG Knowledge** — maintenance manual Q&A
"""
)

if online:
    try:
        farms = get_client().list_farms()
        st.subheader("Registered farms")
        st.dataframe(farms, use_container_width=True, hide_index=True)
    except APIError as exc:
        st.error(str(exc))
else:
    st.warning("Start the backend first:  `uvicorn backend.app.main:app --reload`")
