# SolarOps AI – System Architecture

## 1. Overview

SolarOps AI is an **Agentic Renewable Energy Operations Platform** designed to automate monitoring, forecasting, anomaly detection, and decision-making for distributed solar farms.

It replaces manual operational workflows with a coordinated system of:
- Machine Learning models
- LLM-powered reasoning agents
- Retrieval-Augmented Generation (RAG)
- Human-in-the-loop approvals
- Structured API services

The system is optimized for:
- Operational intelligence
- Explainability
- Safety in automation
- Modular AI agent orchestration

---

## 2. High-Level System Design

The system follows a **layered agentic architecture**:
External Data Sources
   │
   ├── Weather APIs (Open-Meteo, NASA POWER)
   ├── SCADA / Sensor Data (simulated or real)
   ├── Historical Energy Production Data
   └── Maintenance Documentation (PDFs, SOPs)
           │
           ▼
────────────────────────────────────────
        Data Ingestion Layer
────────────────────────────────────────
           │
           ▼
────────────────────────────────────────
        Feature Engineering + ML Layer
────────────────────────────────────────
           │
           ▼
────────────────────────────────────────
        Agentic Intelligence Layer
        (LangGraph Orchestrator)
────────────────────────────────────────
           │
     ┌──────────┼────────────────┬────────────────┐
     ▼          ▼                ▼                ▼
 Weather      Solar            Anomaly          RAG / Root Cause Agent
 Agent        Forecast         Detection        Agent
              Agent            Agent
                        │
                        ▼
────────────────────────────────────────
     Decision & Governance Layer
────────────────────────────────────────
           │
     ┌─────┴─────────────┐
     ▼                   ▼
Human-in-the-loop   Automated Actions
Approval System     (Work Orders, Alerts)
           │
           ▼
────────────────────────────────────────
          Application Layer
────────────────────────────────────────
           │
     ┌─────┴─────────────┐
     ▼                   ▼
 FastAPI Backend    Streamlit Dashboard

---
### 🧱 SolarOps AI – Repository Structure
````
solarops-ai/
│
├── README.md
├── pyproject.toml
├── requirements.txt
├── .env.example
├── docker-compose.yml
├── Makefile
│
├── copilot-instructions.md
├── architecture.md
├── TASKS.md
├── data_schema.md
│
├── docs/
│   ├── domain_overview.md
│   ├── failure_modes.md
│   ├── agent_design.md
│
├── prompts/
│   ├── root_cause.md
│   ├── optimization.md
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── router.py
│   │   │   ├── routes/
│   │   │   │   ├── forecast.py
│   │   │   │   ├── anomaly.py
│   │   │   │   ├── rca.py
│   │   │   │   ├── approvals.py
│   │   │   │   ├── reports.py
│   │   │   │   └── health.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   ├── security.py
│   │   │
│   │   ├── services/
│   │   │   ├── weather_service.py
│   │   │   ├── forecast_service.py
│   │   │   ├── anomaly_service.py
│   │   │   ├── rca_service.py
│   │   │   ├── report_service.py
│   │   │   ├── approval_service.py
│   │   │
│   │   ├── models/
│   │   │   ├── schemas.py
│   │   │   ├── requests.py
│   │   │   ├── responses.py
│   │   │
│   │   ├── db/
│   │   │   ├── session.py
│   │   │   ├── models.py
│   │   │   ├── repository.py
│   │   │
│   │   ├── utils/
│   │       ├── helpers.py
│   │       ├── time.py
│   │
│   ├── tests/
│       ├── test_api.py
│       ├── test_agents.py
│       ├── test_ml.py
│
├── agents/
│   ├── orchestrator/
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── router.py
│   │
│   ├── weather_agent/
│   │   ├── agent.py
│   │   ├── prompts.py
│   │   ├── tools.py
│   │
│   ├── forecasting_agent/
│   │   ├── agent.py
│   │   ├── model.py
│   │   ├── inference.py
│   │   ├── train.py
│   │
│   ├── anomaly_agent/
│   │   ├── agent.py
│   │   ├── detector.py
│   │   ├── features.py
│   │
│   ├── rca_agent/
│   │   ├── agent.py
│   │   ├── reasoning.py
│   │   ├── prompt_templates.py
│   │
│   ├── hitl_agent/
│   │   ├── approval_logic.py
│   │   ├── escalation_rules.py
│   │
│   ├── shared/
│       ├── llm_client.py
│       ├── schemas.py
│       ├── state.py
│
├── ml/
│   ├── training/
│   │   ├── train_forecasting.py
│   │   ├── train_anomaly.py
│   │
│   ├── inference/
│   │   ├── forecast_pipeline.py
│   │   ├── anomaly_pipeline.py
│   │
│   ├── features/
│   │   ├── weather_features.py
│   │   ├── temporal_features.py
│   │
│   ├── evaluation/
│   │   ├── metrics.py
│   │   ├── backtesting.py
│   │
│   ├── experiments/
│
├── rag/
│   ├── ingestion/
│   │   ├── load_docs.py
│   │   ├── parse_pdf.py
│   │
│   ├── indexing/
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │
│   ├── retrieval/
│   │   ├── retriever.py
│   │   ├── reranker.py
│   │
│   ├── generation/
│   │   ├── rag_chain.py
│   │   ├── prompts.py
│   │
│   ├── data/
│       ├── manuals/
│
├── workflows/
│   ├── daily_operations_graph.py
│   ├── anomaly_response_graph.py
│   ├── maintenance_flow_graph.py
│   ├── state_definitions.py
│
├── streamlit_app/
│   ├── app.py
│   │
│   ├── pages/
│   │   ├── 1_dashboard.py
│   │   ├── 2_forecasts.py
│   │   ├── 3_anomalies.py
│   │   ├── 4_rca_explanations.py
│   │   ├── 5_approvals.py
│   │   ├── 6_rag_knowledge.py
│   │
│   ├── components/
│   │   ├── charts.py
│   │   ├── tables.py
│   │   ├── cards.py
│   │   ├── layout.py
│   │
│   ├── services/
│   │   ├── api_client.py
│   │
│   ├── utils/
│       ├── formatters.py
│       ├── constants.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── synthetic/
│   ├── schemas/
│
├── infra/
│   ├── docker/
│   │   ├── backend.Dockerfile
│   │   ├── streamlit.Dockerfile
│   │
│   ├── kubernetes/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │
│   ├── terraform/
│   │   ├── main.tf
│   │
│   ├── nginx/
│       ├── nginx.conf
│
├── scripts/
│   ├── run_backend.sh
│   ├── run_streamlit.sh
│   ├── train_models.sh
│   ├── load_data.sh
│
├── configs/
│   ├── app_config.yaml
│   ├── model_config.yaml
│   ├── agent_config.yaml
│
└── logs/
    ├── agent_logs/
    ├── ml_logs/
    ├── api_logs/
````
---

## 3. Core Architectural Principles

### 3.1 Separation of Concerns
Each system layer has a strict responsibility:
- Data ingestion ≠ ML inference ≠ Agent reasoning ≠ UI rendering

---

### 3.2 Agent Isolation
Each AI agent:
- Has a single responsibility
- Operates on structured inputs/outputs
- Does NOT directly call other agents
- Communicates only via LangGraph state

---

### 3.3 Deterministic Data Contracts
All inter-component communication uses:
- Pydantic models (backend)
- Typed schemas (agents)
- Versioned ML feature sets

---

### 3.4 Event-Driven Orchestration
LangGraph acts as a **central state machine**, not a loose pipeline.

- Each node is deterministic where possible
- LLMs are used only for reasoning/explanation tasks
- Control flow is explicit and auditable

---

## 4. Core System Components

---

## 4.1 Weather Intelligence Subsystem

### Responsibility
Convert raw meteorological data into actionable operational insights.

### Inputs
- Open-Meteo API
- NASA POWER dataset

### Outputs
- Cloud coverage score
- Irradiance estimate
- Temperature stress index
- Wind risk indicator

---

## 4.2 Forecasting Subsystem

### Responsibility
Predict solar energy production per farm.

### Model Types
- LightGBM (primary baseline)
- XGBoost (optional alternative)

### Inputs
- Historical energy output
- Weather features
- Temporal features

### Outputs
- Daily forecast
- Confidence interval
- Peak production window

---

## 4.3 Anomaly Detection Subsystem

### Responsibility
Detect deviations from expected system behavior.

### Methods
- Isolation Forest
- Statistical residual analysis

### Inputs
- Forecast vs actual production
- SCADA-like telemetry

### Outputs
- anomaly_score
- severity classification
- affected farm IDs

---

## 4.4 Root Cause Analysis (RCA) Agent

### Responsibility
Explain *why* anomalies occur.

### Approach
Hybrid reasoning system:
- Feature importance heuristics
- LLM-based explanation synthesis
- Context retrieval from historical incidents

### Outputs
- ranked root causes
- confidence scores
- natural language explanation

---

## 4.5 RAG Knowledge Subsystem

### Responsibility
Provide grounded maintenance knowledge.

### Data Sources
- Maintenance manuals
- SOP documents
- Equipment datasheets
- Historical incident logs

### Pipeline
1. Document ingestion
2. Chunking
3. Embedding generation
4. Vector storage
5. Retrieval + reranking
6. LLM response generation

---

## 4.6 Human-in-the-Loop (HITL) System

### Responsibility
Ensure safe execution of operational decisions.

### Trigger Conditions
- High severity anomaly
- Work order creation
- External system actions

### Workflow
1. System proposes action
2. Human reviews
3. Decision recorded
4. Action executed or rejected

### States
- PENDING
- APPROVED
- REJECTED
- MODIFIED

---

## 4.7 LangGraph Orchestration Layer

### Responsibility
Coordinate all agents into a unified workflow.

### State Flow

Weather Node
    ↓
Forecast Node
    ↓
Anomaly Detection Node
    ↓
Conditional RCA Node
    ↓
Report Generation Node
    ↓
HITL Node (if required)


### Key Design Rule
All system intelligence flows through a **single state object**.

---

## 5. Data Flow Architecture

### 5.1 Ingestion Flow
- APIs → Raw Data Store → Feature Engineering Layer

### 5.2 Processing Flow
- Features → ML Models → Predictions → Agents

### 5.3 Decision Flow
- Agent outputs → LangGraph → HITL → Actions

### 5.4 Presentation Flow
- Backend API → Streamlit Frontend Dashboard

---

## 6. Backend Architecture (FastAPI)

### Layers

- API Layer (routes only)
- Service Layer (business logic)
- ML Layer (inference pipelines)
- Agent Layer (LangGraph execution)
- DB Layer (repositories)

### Key Principle
No ML or agent logic is allowed inside API routes.

---

## 7. Frontend Architecture (Streamlit Dashboard)

### Responsibilities
- Visualization of solar farm status
- Display forecasts and anomalies
- Render RCA explanations
- Manage approval workflows

### Design Principle
Frontend is **purely a presentation layer**.

No business logic or ML logic resides in UI components.

---

## 8. Storage Architecture

### 8.1 PostgreSQL
- farm metadata
- forecasts
- anomaly logs
- approval history

### 8.2 TimescaleDB (optional upgrade)
- time-series sensor data

### 8.3 Vector Database (Qdrant / FAISS)
- RAG embeddings
- maintenance knowledge base

---

## 9. Agent Communication Model

All agents communicate via:
Shared State Object
{
farm_id,
timestamp,
weather_data,
forecast,
anomaly_score,
rca_result,
approval_status,
metadata
}


No direct function-to-function agent calls are allowed.

---

## 10. Non-Functional Requirements

### 10.1 Observability
- Logging for every agent execution step
- Traceable request IDs
- Basic performance metrics per agent

### 10.2 Reliability
- Graceful failure handling in LangGraph nodes
- Fallback logic for missing data

### 10.3 Scalability
- Stateless API design
- Independent agent execution
- Modular ML pipelines

---

## 11. Security Constraints

- No hardcoded secrets
- Environment-based configuration only
- Input validation on all external APIs
- Sanitization of LLM outputs before downstream use

---

## 12. System Summary

SolarOps AI is designed as a **production-style agentic decision system** that:

- Converts raw environmental + operational data into insights
- Uses ML for prediction
- Uses agents for reasoning
- Uses LLMs for explanation
- Uses HITL for safety
- Uses LangGraph for orchestration

The system simulates a real-world **Solar Operations Control Center AI Assistant**.

---

## 13. Design Philosophy
- Technology decisions are defined in TECH_STACK.md.
    - Developers must not introduce new frameworks or Python libraries without updating TECH_STACK.md and documenting the rationale.
    
> “Every decision in the system must be traceable, explainable, and grounded in structured data.”

Simplicity is preferred over complexity, as long as modularity and clarity are preserved.