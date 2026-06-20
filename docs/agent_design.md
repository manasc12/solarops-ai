# Agent Design — Multi-Agent Architecture

SolarOps is built as a set of single-responsibility agents coordinated by a
LangGraph orchestrator. Agents never call each other directly; they communicate
only through a shared, typed `SystemState` object. Every agent input and output
is a Pydantic-validated, JSON-serializable schema.

## Shared state

`SystemState` (defined in `backend/app/models/schemas.py`, re-exported by
`workflows/state_definitions.py` and `agents/shared/state.py`) is the single
object threaded through the graph. Each node reads the fields it needs and writes
its result back:

```
farm_id → weather → forecast → anomaly → rca → report → approval → errors[]
```

Nodes are pure where possible: they take the state, do their work via a service,
and return an updated state. Failures are captured into `state.errors` rather
than raising, so one agent failing never crashes the pipeline.

## Agents

### 1. Weather Intelligence Agent (`agents/weather_agent/`)
Acquires and interprets meteorological context (cloud impact, temperature
stress, wind risk, irradiance quality). Pure data + light feature derivation; no
ML or LLM logic. Backed by `weather_service` (Open-Meteo with a deterministic
mock fallback).

### 2. Forecasting Agent (`agents/forecasting_agent/`)
Predicts next-horizon energy generation using a LightGBM model with engineered
temporal + weather features. Produces a `SolarForecast` with confidence bounds.
Training and inference are separated; artifacts are versioned on disk.

### 3. Anomaly Detection Agent (`agents/anomaly_agent/`)
Computes the weather-adjusted **performance deviation** and inverter health, then
scores it with an IsolationForest (`detection_method = ISOLATION_FOREST`).
Emits an `AnomalyDetectionResult` with `anomaly_score`, `severity`, and
`deviation_pct`. The vector is **scale-invariant** (relative deviation + inverter
status), so a healthy farm is never flagged merely for high production.

### 4. Root Cause Analysis Agent (`agents/rca_agent/`)
Reasons over the anomaly signature and weather context to produce a ranked list
of likely causes with weights (`RCAResult`). LLM-based when an API key is
configured; otherwise a deterministic template-reasoning fallback keeps it fully
offline and reproducible. LLM use is confined to reasoning/summarization.

### 5. Human-in-the-Loop Agent (`agents/hitl_agent/`)
Models approval as a **blocking node**. Any HIGH-severity finding (or any action
with external impact) opens an `ApprovalRequest` in `PENDING` state and halts the
automated path until a human approves, rejects, or modifies it. All decisions are
logged for auditability.

### 6. Orchestrator (`agents/orchestrator/`)
Builds the LangGraph `StateGraph(SystemState)`. Conditional routing lives here
and only here:

- `route_after_anomaly`: run RCA if `anomaly_score >= 0.6`, else go straight to report.
- `route_after_report`: open the HITL gate if severity is HIGH, else END.

A sequential fallback executes the same node order when LangGraph is unavailable,
so the pipeline runs in any environment.

## Design principles enforced

- **Single responsibility** per agent.
- **Structured I/O only** — no free-form strings passed between agents.
- **Graceful degradation** — heavy/optional dependencies (LLM, LangGraph, vector
  DB) have deterministic fallbacks; the system never hard-requires API keys.
- **Auditability** — every agent step is logged as structured JSON.
