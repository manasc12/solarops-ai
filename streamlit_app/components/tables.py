"""Reusable table render functions (presentation only)."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def approvals_table(approvals: list[dict]) -> None:
    if not approvals:
        st.success("No items in the approval queue.")
        return
    df = pd.DataFrame(
        [
            {
                "Request": a.get("request_id"),
                "Farm": a.get("farm_id"),
                "Action": a.get("action_type"),
                "Severity": a.get("severity"),
                "Status": a.get("status"),
                "Proposed by": a.get("proposed_by"),
            }
            for a in approvals
        ]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)


def chunks_table(chunks: list[dict]) -> None:
    if not chunks:
        return
    for c in chunks:
        src = c.get("metadata", {}).get("source", c.get("doc_id", ""))
        with st.expander(f"📄 {src} — {c.get('chunk_id', '')}"):
            st.write(c.get("content", ""))
