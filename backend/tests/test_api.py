"""API contract tests via FastAPI TestClient.

Verifies the global response envelope, endpoint behaviour, and the HITL flow.
"""

from __future__ import annotations


def _assert_envelope(payload: dict) -> None:
    assert set(["status", "data", "error", "timestamp"]).issubset(payload.keys())


def test_health(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    _assert_envelope(body)
    assert body["status"] == "success"
    assert body["data"]["status"] == "healthy"


def test_list_farms(client):
    body = client.get("/api/v1/farms").json()
    _assert_envelope(body)
    assert len(body["data"]) >= 1


def test_forecast_endpoint(client):
    body = client.post("/api/v1/forecast", json={"farm_id": "FARM_001"}).json()
    _assert_envelope(body)
    assert body["data"]["predicted_energy_kwh"] > 0


def test_unknown_farm_returns_error_envelope(client):
    resp = client.post("/api/v1/forecast", json={"farm_id": "DOES_NOT_EXIST"})
    assert resp.status_code == 404
    body = resp.json()
    _assert_envelope(body)
    assert body["status"] == "error"
    assert body["error"]["message"]


def test_report_pipeline_and_hitl_flow(client):
    # Run full workflow on the faulted farm -> should create a pending approval.
    report = client.post("/api/v1/report", json={"farm_id": "FARM_002"}).json()
    assert report["data"]["approval_status"] == "PENDING"

    pending = client.get("/api/v1/approvals").json()["data"]
    assert len(pending) >= 1
    request_id = pending[0]["request_id"]

    decided = client.post(
        "/api/v1/approvals/decision",
        json={"request_id": request_id, "decision": "APPROVED", "reviewer": "tester"},
    ).json()
    assert decided["data"]["status"] == "APPROVED"

    detail = client.get(f"/api/v1/approvals/{request_id}").json()
    assert detail["data"]["history"][0]["decision"] == "APPROVED"


def test_rag_query_endpoint(client):
    body = client.post("/api/v1/rag/query", json={"query": "inverter failure", "top_k": 3}).json()
    _assert_envelope(body)
    assert "answer" in body["data"]
    assert isinstance(body["data"]["retrieved_chunks"], list)
