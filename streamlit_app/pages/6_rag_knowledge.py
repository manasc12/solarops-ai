"""RAG knowledge page: maintenance manual Q&A."""

from __future__ import annotations

import streamlit as st

from streamlit_app.components.layout import backend_status, page_header
from streamlit_app.components.tables import chunks_table
from streamlit_app.services.api_client import APIError, get_client

page_header("Maintenance Knowledge — grounded RAG Q&A")
backend_status()

query = st.text_input(
    "Ask a maintenance question",
    value="What should I do when an inverter reports a FAILURE status?",
)
top_k = st.sidebar.slider("Chunks to retrieve", 1, 8, 4)

if st.button("Ask", type="primary") and query:
    try:
        st.session_state["rag_result"] = get_client().rag_query(query, top_k)
    except APIError as exc:
        st.error(str(exc))

result = st.session_state.get("rag_result")
if not result:
    st.info("Ask a question grounded in the maintenance manuals.")
    st.stop()

st.subheader("Answer")
st.write(result["answer"])
st.caption(f"Confidence: {result.get('confidence', 0):.2f}")

st.subheader("Retrieved context")
chunks_table(result.get("retrieved_chunks", []))
