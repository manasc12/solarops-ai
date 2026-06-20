"""RCA explanations page."""

from __future__ import annotations

import streamlit as st

from streamlit_app.components.charts import cause_weights_chart
from streamlit_app.components.layout import backend_status, farm_selector, page_header
from streamlit_app.services.api_client import APIError, get_client

page_header("Root Cause Analysis — grounded reasoning")
backend_status()
farm_id = farm_selector(key="rca_farm")

if farm_id and st.sidebar.button("Run RCA", type="primary"):
    try:
        st.session_state["rca_result"] = get_client().rca(farm_id)
    except APIError as exc:
        st.error(str(exc))

rca = st.session_state.get("rca_result")
if not rca:
    st.info("Select a farm and run root cause analysis.")
    st.stop()

st.subheader(f"Farm {rca['farm_id']}")
st.metric("Confidence", f"{rca['confidence_score']:.0%}")
st.write(rca["explanation_text"])

st.subheader("Ranked causes")
cause_weights_chart(rca)

st.subheader("Supporting signals")
for signal in rca.get("supporting_signals", []):
    st.write(f"- {signal}")
