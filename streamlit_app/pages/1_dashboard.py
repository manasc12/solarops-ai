"""Dashboard page: run the full daily-operations workflow for a farm."""

from __future__ import annotations

import streamlit as st

from streamlit_app.components.cards import anomaly_cards, forecast_cards
from streamlit_app.components.charts import anomaly_gauge, cause_weights_chart, forecast_band_chart
from streamlit_app.components.layout import backend_status, farm_selector, page_header
from streamlit_app.services.api_client import APIError, get_client

page_header("Dashboard — end-to-end operations workflow")
backend_status()
farm_id = farm_selector(key="dashboard_farm")

if farm_id and st.sidebar.button("Run daily operations", type="primary"):
    with st.spinner("Executing LangGraph workflow..."):
        try:
            result = get_client().run_report(farm_id)
        except APIError as exc:
            st.error(str(exc))
            st.stop()
    st.session_state["dashboard_result"] = result

result = st.session_state.get("dashboard_result")
if not result:
    st.info("Select a farm and run the daily operations workflow.")
    st.stop()

st.subheader(f"Farm {result['farm_id']}")
left, right = st.columns(2)
with left:
    forecast_cards(result.get("forecast"))
    forecast_band_chart(result.get("forecast"))
with right:
    anomaly_cards(result.get("anomaly"))
    anomaly_gauge(result.get("anomaly"))

if result.get("rca"):
    st.subheader("Root cause analysis")
    st.write(result["rca"]["explanation_text"])
    cause_weights_chart(result["rca"])

st.subheader("Governance")
st.write(f"Approval status: **{result.get('approval_status')}**")

st.subheader("Execution trace")
st.dataframe(result.get("trace", []), use_container_width=True, hide_index=True)

with st.expander("Full report"):
    st.markdown(result.get("report") or "_No report_")
