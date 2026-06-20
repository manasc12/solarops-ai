"""Anomalies page."""

from __future__ import annotations

import streamlit as st

from streamlit_app.components.cards import anomaly_cards
from streamlit_app.components.charts import anomaly_gauge
from streamlit_app.components.layout import backend_status, farm_selector, page_header
from streamlit_app.services.api_client import APIError, get_client

page_header("Anomalies — forecast vs actual deviation")
backend_status()
farm_id = farm_selector(key="anomaly_farm")

if farm_id and st.sidebar.button("Detect anomaly", type="primary"):
    try:
        st.session_state["anomaly_result"] = get_client().anomaly(farm_id)
    except APIError as exc:
        st.error(str(exc))

anomaly = st.session_state.get("anomaly_result")
if not anomaly:
    st.info("Select a farm and run anomaly detection.")
    st.stop()

st.subheader(f"Farm {anomaly['farm_id']}")
c1, c2 = st.columns(2)
with c1:
    anomaly_cards(anomaly)
with c2:
    anomaly_gauge(anomaly)
st.json(anomaly)
