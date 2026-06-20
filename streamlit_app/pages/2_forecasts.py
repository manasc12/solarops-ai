"""Forecasts page."""

from __future__ import annotations

import streamlit as st

from streamlit_app.components.cards import forecast_cards
from streamlit_app.components.charts import forecast_band_chart
from streamlit_app.components.layout import backend_status, farm_selector, page_header
from streamlit_app.services.api_client import APIError, get_client

page_header("Forecasts — solar production prediction")
backend_status()
farm_id = farm_selector(key="forecast_farm")
horizon = st.sidebar.slider("Horizon (hours)", 6, 72, 24, step=6)

if farm_id and st.sidebar.button("Generate forecast", type="primary"):
    try:
        st.session_state["forecast_result"] = get_client().forecast(farm_id, horizon)
    except APIError as exc:
        st.error(str(exc))

forecast = st.session_state.get("forecast_result")
if not forecast:
    st.info("Select a farm and generate a forecast.")
    st.stop()

st.subheader(f"Farm {forecast['farm_id']} — model {forecast['model_version']}")
forecast_cards(forecast)
forecast_band_chart(forecast)
st.json(forecast)
