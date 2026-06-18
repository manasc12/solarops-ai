# SolarOps AI – Data Schema & Correctness Contracts

## Purpose

This document defines all **canonical data structures** used across the SolarOps AI system.

It guarantees:
- schema consistency across agents
- ML reproducibility
- safe LangGraph orchestration
- structured LLM outputs
- strict API contracts
- elimination of unstructured data flow

---

# ⚠️ Global Schema Rules (STRICT)

- All data MUST conform to defined schemas
- No free-form dictionaries in inter-module communication
- All agent outputs MUST be JSON-serializable
- All timestamps MUST be ISO-8601
- All numeric values MUST include units where applicable
- Missing values MUST be explicitly null (never omitted)
- All schemas MUST be versioned (v1 initial)

---

# 🌤 1. Weather Data Schema

## WeatherData (v1)

Represents normalized weather conditions per solar farm.

```python
WeatherData
````

### Fields

| Field              | Type                | Description                          |
| ------------------ | ------------------- | ------------------------------------ |
| farm_id            | string              | Unique identifier for solar farm     |
| timestamp          | datetime (ISO-8601) | Observation time                     |
| temperature_c      | float               | Ambient temperature (°C)             |
| cloud_cover_pct    | float               | Cloud coverage percentage            |
| irradiance_wm2     | float               | Solar irradiance                     |
| wind_speed_ms      | float               | Wind speed                           |
| precipitation_prob | float               | Probability of rain (0–1)            |
| uv_index           | float               | UV radiation index                   |
| source             | string              | API source (Open-Meteo / NASA POWER) |

---

# ☀️ 2. Forecast Schema

## SolarForecast (v1)

Represents predicted energy generation.

### Fields

| Field                | Type     | Description              |
| -------------------- | -------- | ------------------------ |
| farm_id              | string   | Solar farm identifier    |
| timestamp            | datetime | Forecast generation time |
| predicted_energy_kwh | float    | Predicted energy output  |
| confidence_lower     | float    | Lower bound estimate     |
| confidence_upper     | float    | Upper bound estimate     |
| peak_generation_time | datetime | Expected peak production |
| model_version        | string   | ML model version         |

---

# 📈 3. Actual Energy Observation Schema

## EnergyObservation (v1)

Represents actual solar farm output.

### Fields

| Field               | Type     | Description             |
| ------------------- | -------- | ----------------------- |
| farm_id             | string   | Solar farm identifier   |
| timestamp           | datetime | Measurement time        |
| energy_kwh          | float    | Actual generated energy |
| inverter_status     | string   | OK / DEGRADED / FAILURE |
| panel_temperature_c | float    | Panel temperature       |
| voltage_v           | float    | Output voltage          |
| current_a           | float    | Output current          |

---

# 🚨 4. Anomaly Schema

## AnomalyDetectionResult (v1)

Represents detected deviations.

### Fields

| Field            | Type     | Description                            |
| ---------------- | -------- | -------------------------------------- |
| farm_id          | string   | Solar farm identifier                  |
| timestamp        | datetime | Detection time                         |
| anomaly_score    | float    | 0–1 severity score                     |
| severity         | enum     | LOW / MEDIUM / HIGH                    |
| deviation_pct    | float    | Forecast vs actual deviation           |
| detection_method | string   | IsolationForest / Statistical / Hybrid |
| explanation_stub | string   | Preliminary non-LLM reason             |

---

# 🔍 5. Root Cause Analysis Schema

## RCAResult (v1)

LLM-generated explanation of anomalies.

### Fields

| Field              | Type         | Description                |
| ------------------ | ------------ | -------------------------- |
| farm_id            | string       | Solar farm identifier      |
| timestamp          | datetime     | Analysis time              |
| root_causes        | list[string] | Ranked causes              |
| cause_weights      | list[float]  | Contribution scores (0–1)  |
| confidence_score   | float        | RCA confidence             |
| explanation_text   | string       | Human-readable explanation |
| supporting_signals | list[string] | Evidence used              |

---

# 🤖 6. Agent State Schema (LangGraph Core)

## SystemState (v1)

This is the **central shared state object used across all agents**.

### Fields
````python
SystemState
````

| Field           | Type                   | Description            |
| --------------- | ---------------------- | ---------------------- |
| farm_id         | string                 | Active farm            |
| timestamp       | datetime               | Execution time         |
| weather         | WeatherData            | Weather context        |
| forecast        | SolarForecast          | ML prediction          |
| actual          | EnergyObservation      | Real output            |
| anomaly         | AnomalyDetectionResult | Detected anomalies     |
| rca             | RCAResult              | Root cause analysis    |
| approval_status | ApprovalStatus         | HITL state             |
| report          | string                 | Final generated report |
| metadata        | dict                   | Additional system info |

---

# 👨‍💼 7. Human-in-the-Loop Schema

## ApprovalRequest (v1)

### Fields

| Field       | Type     | Description                              |
| ----------- | -------- | ---------------------------------------- |
| request_id  | string   | Unique approval ID                       |
| farm_id     | string   | Target solar farm                        |
| action_type | string   | WorkOrder / Alert / Shutdown             |
| severity    | enum     | LOW / MEDIUM / HIGH                      |
| description | string   | Action explanation                       |
| proposed_by | string   | Agent ID                                 |
| timestamp   | datetime | Request time                             |
| status      | enum     | PENDING / APPROVED / REJECTED / MODIFIED |

---

## ApprovalDecision (v1)

### Fields

| Field      | Type     | Description                    |
| ---------- | -------- | ------------------------------ |
| request_id | string   | Linked approval request        |
| decision   | enum     | APPROVED / REJECTED / MODIFIED |
| reviewer   | string   | Human operator ID              |
| timestamp  | datetime | Decision time                  |
| notes      | string   | Optional justification         |

---

# 📚 8. RAG Schema

## DocumentChunk (v1)

### Fields

| Field     | Type   | Description              |
| --------- | ------ | ------------------------ |
| doc_id    | string | Source document ID       |
| chunk_id  | string | Chunk identifier         |
| content   | string | Text chunk               |
| embedding | vector | Embedding representation |
| metadata  | dict   | Document metadata        |

---

## RAGQueryResult (v1)

### Fields

| Field            | Type                | Description              |
| ---------------- | ------------------- | ------------------------ |
| query            | string              | User question            |
| retrieved_chunks | list[DocumentChunk] | Relevant context         |
| answer           | string              | LLM response             |
| confidence       | float               | Answer reliability score |

---

# 📊 9. Forecast Error Schema

## ForecastEvaluation (v1)

### Fields

| Field     | Type     | Description                      |
| --------- | -------- | -------------------------------- |
| farm_id   | string   | Solar farm                       |
| timestamp | datetime | Evaluation time                  |
| mae       | float    | Mean absolute error              |
| rmse      | float    | Root mean squared error          |
| mape      | float    | Percentage error                 |
| bias      | float    | Systematic over/under prediction |

---

# 🔗 10. API Response Standard (GLOBAL CONTRACT)

All API responses MUST follow (JSON):

````JSON
{
  "status": "success | error",
  "data": {},
  "error": {
    "code": "",
    "message": ""
  },
  "timestamp": "ISO-8601"
}
````
---

# 🧠 11. Data Integrity Rules

## Required guarantees:

* Every farm_id must exist in master registry
* Forecast timestamps must align with weather timestamps
* Anomaly detection must reference both forecast and actual
* RCA must only trigger if anomaly_score > threshold
* No null propagation without explicit handling

---

# ⚠️ 12. Schema Validation Rules

* All inputs MUST be validated using Pydantic (backend)
* All agent outputs MUST be schema-validated before passing to next node
* LangGraph state transitions MUST reject invalid schemas
* RAG outputs MUST include source attribution

---

# 🚀 13. System Truth Statement

This schema file is the **single source of truth** for all system data.

Any module that violates these contracts is considered invalid.

The system prioritizes:

* consistency
* traceability
* structured reasoning
* deterministic data flow

over flexibility or ad-hoc outputs.

