"""Centralized backend API client.

The ONLY place in the frontend that performs HTTP. Streamlit pages and
components call these typed methods; they never issue requests inline. Every
backend response uses the standard envelope, unwrapped here into plain data.
"""

from __future__ import annotations

import os
from typing import Any

import requests

_DEFAULT_TIMEOUT = 60


class APIError(Exception):
    """Raised when the backend returns an error envelope or is unreachable."""


class APIClient:
    def __init__(self, base_url: str | None = None) -> None:
        base = base_url or os.environ.get("BACKEND_URL", "http://localhost:8000")
        self._base = f"{base.rstrip('/')}/api/v1"

    # ── low-level ───────────────────────────────────────────────────────────
    def _unwrap(self, resp: requests.Response) -> Any:
        try:
            payload = resp.json()
        except ValueError as exc:
            raise APIError(f"Invalid response ({resp.status_code})") from exc
        if isinstance(payload, dict) and payload.get("status") == "error":
            err = payload.get("error") or {}
            raise APIError(err.get("message", "Unknown error"))
        if resp.status_code >= 400:
            raise APIError(f"HTTP {resp.status_code}")
        return payload.get("data") if isinstance(payload, dict) else payload

    def _get(self, path: str) -> Any:
        try:
            return self._unwrap(requests.get(f"{self._base}{path}", timeout=_DEFAULT_TIMEOUT))
        except requests.RequestException as exc:
            raise APIError(f"Backend unreachable: {exc}") from exc

    def _post(self, path: str, body: dict) -> Any:
        try:
            return self._unwrap(
                requests.post(f"{self._base}{path}", json=body, timeout=_DEFAULT_TIMEOUT)
            )
        except requests.RequestException as exc:
            raise APIError(f"Backend unreachable: {exc}") from exc

    # ── health / farms ──────────────────────────────────────────────────────
    def health(self) -> dict:
        return self._get("/health")

    def list_farms(self) -> list[dict]:
        return self._get("/farms")

    # ── forecast / anomaly / rca ────────────────────────────────────────────
    def forecast(self, farm_id: str, horizon_hours: int = 24) -> dict:
        return self._post("/forecast", {"farm_id": farm_id, "horizon_hours": horizon_hours})

    def anomaly(self, farm_id: str) -> dict:
        return self._post("/anomaly", {"farm_id": farm_id})

    def rca(self, farm_id: str) -> dict:
        return self._post("/rca", {"farm_id": farm_id})

    # ── pipeline / report ───────────────────────────────────────────────────
    def run_report(self, farm_id: str) -> dict:
        return self._post("/report", {"farm_id": farm_id})

    def latest_report(self, farm_id: str) -> dict:
        return self._get(f"/report/{farm_id}")

    # ── approvals ───────────────────────────────────────────────────────────
    def pending_approvals(self) -> list[dict]:
        return self._get("/approvals")

    def all_approvals(self) -> list[dict]:
        return self._get("/approvals/all")

    def decide_approval(
        self, request_id: str, decision: str, reviewer: str, notes: str = ""
    ) -> dict:
        return self._post(
            "/approvals/decision",
            {"request_id": request_id, "decision": decision, "reviewer": reviewer, "notes": notes},
        )

    # ── rag ─────────────────────────────────────────────────────────────────
    def rag_query(self, query: str, top_k: int = 4) -> dict:
        return self._post("/rag/query", {"query": query, "top_k": top_k})


_client: APIClient | None = None


def get_client() -> APIClient:
    global _client
    if _client is None:
        _client = APIClient()
    return _client
