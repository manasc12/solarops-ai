"""Shared layout helpers: page header and farm selector (presentation only)."""

from __future__ import annotations

import streamlit as st

from streamlit_app.services.api_client import APIError, get_client
from streamlit_app.utils.constants import APP_TITLE


def page_header(subtitle: str) -> None:
    st.set_page_config(page_title="SolarOps AI", page_icon="☀️", layout="wide")
    st.title(APP_TITLE)
    st.caption(subtitle)


def backend_status() -> bool:
    try:
        get_client().health()
        st.sidebar.success("Backend: connected")
        return True
    except APIError as exc:
        st.sidebar.error(f"Backend unavailable\n\n{exc}")
        return False


def farm_selector(key: str = "farm") -> str | None:
    try:
        farms = get_client().list_farms()
    except APIError as exc:
        st.sidebar.error(f"Could not load farms: {exc}")
        return None
    options = {f"{f['name']} ({f['farm_id']})": f["farm_id"] for f in farms}
    if not options:
        st.sidebar.warning("No farms registered.")
        return None
    label = st.sidebar.selectbox("Solar farm", list(options.keys()), key=key)
    return options[label]
