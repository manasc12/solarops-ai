"""Approvals page: human-in-the-loop action queue."""

from __future__ import annotations

import streamlit as st

from streamlit_app.components.cards import severity_badge, status_badge
from streamlit_app.components.layout import backend_status, page_header
from streamlit_app.components.tables import approvals_table
from streamlit_app.services.api_client import APIError, get_client

page_header("Approvals — human-in-the-loop governance")
backend_status()
client = get_client()

try:
    pending = client.pending_approvals()
except APIError as exc:
    st.error(str(exc))
    st.stop()

st.subheader("Pending queue")
approvals_table(pending)

if pending:
    st.subheader("Review an action")
    options = {f"{a['request_id']} — {a['farm_id']} ({a['severity']})": a for a in pending}
    selected_label = st.selectbox("Select request", list(options.keys()))
    item = options[selected_label]

    st.markdown(severity_badge(item["severity"]), unsafe_allow_html=True)
    st.markdown(status_badge(item["status"]), unsafe_allow_html=True)
    st.write(item.get("description", ""))

    reviewer = st.text_input("Reviewer ID", value="operator")
    notes = st.text_area("Notes", value="")
    col1, col2, col3 = st.columns(3)
    decision = None
    if col1.button("✅ Approve", type="primary"):
        decision = "APPROVED"
    if col2.button("❌ Reject"):
        decision = "REJECTED"
    if col3.button("✏️ Modify"):
        decision = "MODIFIED"

    if decision:
        try:
            result = client.decide_approval(item["request_id"], decision, reviewer, notes)
            st.success(f"Request {result['request_id']} -> {result['status']}")
            st.rerun()
        except APIError as exc:
            st.error(str(exc))

st.subheader("All requests (audit)")
try:
    approvals_table(client.all_approvals())
except APIError as exc:
    st.error(str(exc))
