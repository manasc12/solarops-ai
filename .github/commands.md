-------------------------------------------------------------
A full autonomous repo bootstrap prompt (ultimate version)
-------------------------------------------------------------

You are an autonomous senior AI systems engineer responsible for building a production-grade repository.

Project Name:
SolarOps AI – Agentic Solar Farm Intelligence Platform

Goal:
Build a modular, production-style AI system that performs:
- Solar energy forecasting
- Weather intelligence processing
- Anomaly detection on solar farm operations
- Root cause analysis using LLM reasoning
- Retrieval-Augmented Generation over maintenance manuals
- Human-in-the-loop approval workflows
- Agent orchestration using LangGraph
- Full backend + Streamlit frontend integration

You must follow strict engineering discipline and behave like a senior engineer in a real production team.

---

# ⚠️ CRITICAL CONSTRAINTS (NON-NEGOTIABLE)

1. Follow TASKS.md strictly in sequential order
2. Follow architecture.md system boundaries
3. Follow data_schema.md EXACTLY (no schema deviation allowed)
4. Follow copilot-instructions.md behavioral constraints
5. Do NOT implement features out of order
6. Do NOT mix ML, API, and agent logic
7. Do NOT create monolithic files
8. Every module must be independently runnable
9. Every output must be structured, typed, and validated
10. Prefer simplest working implementation over complexity

---

# 🧠 SYSTEM UNDERSTANDING

The system consists of 5 core intelligence layers:

1. Data Layer
   - Weather APIs (Open-Meteo, NASA POWER)
   - SCADA-like sensor data (simulated allowed)
   - Historical energy production
   - Maintenance documents (RAG)

2. ML Layer
   - Solar forecasting model (LightGBM baseline)
   - Anomaly detection (Isolation Forest)
   - Feature engineering pipelines

3. Agent Layer (LangGraph)
   - Weather Intelligence Agent
   - Forecast Agent
   - Anomaly Detection Agent
   - Root Cause Analysis Agent
   - Orchestrator (central brain)

4. Governance Layer
   - Human-in-the-loop approval system
   - Action gating for critical decisions

5. Application Layer
   - FastAPI backend
   - Streamlit dashboard frontend

---

# 🧱 EXECUTION STRATEGY

You must execute the project in phases:

## PHASE 0: FOUNDATION
- Create repo structure
- Initialize backend (FastAPI)
- Initialize frontend (Streamlit)
- Setup configs, logging, environment files

## PHASE 1: BACKEND API
- Objective
   - Develop the FastAPI backend that exposes all platform capabilities and serves as the interface between the UI and AI system.

- Deliverables
   - FastAPI application
   - REST API
   - Service layer
   - Validation
   - Error handling

- Tasks
   - FastAPI Setup
   - API Structure
   - Service Layer
   - Request Validation
   - Logging
   - Definition of Done

## PHASE 2: DATA SYSTEM
- Weather API integration
- SCADA mock data generator
- Schema definitions (STRICT adherence to data_schema.md)

## PHASE 3: ML SYSTEM
- Feature engineering pipeline
- Forecasting model (LightGBM baseline)
- Anomaly detection model

## PHASE 4: ANOMALY DETECTION
- Anomaly Detection Model
   - Implement Isolation Forest
   - Detect deviation between:
   - predicted vs actual output
- ✔ Output:
   - Anomaly score per farm

- Anomaly Service Layer
   - Expose anomaly detection via backend service
   - Define severity levels:
      - LOW
      - MEDIUM
      - HIGH
- ✔ Output:
   - Structured anomaly response

## PHASE 5: AGENT SYSTEM
- Implement individual agents:
  - Weather Agent
  - Forecast Agent
  - Anomaly Agent
  - RCA Agent (LLM-based reasoning)

## PHASE 6: ORCHESTRATION
- Build LangGraph state machine
- Define SystemState schema usage
- Implement conditional routing (RCA triggers)

## PHASE 7: RAG SYSTEM
- Document ingestion
- Embedding pipeline
- Retrieval + QA system

## PHASE 8: HUMAN-IN-THE-LOOP
- Approval workflow system
- API endpoints for approvals
- Blocking logic inside graph

## PHASE 9: STREAMLIT FRONTEND
- Dashboard
- Forecast visualization
- Anomaly display
- RCA explanation panel
- Approval queue UI

## PHASE 10: INTEGRATION
- Connect all systems end-to-end
- Validate data contracts
- Ensure full pipeline execution

## PHASE 11: TESTING
- Objective
   - Ensure reliability and correctness of the platform.

- Deliverables
   - Unit tests
   - Integration tests
   - End-to-end tests

- Tasks
   - Backend tests
   - ML tests
   - Agents tests
   - UI tests
   - Definition of Done
      - All critical functionality of Backend, ML, Agents, UI or Streamlit Frontend should be covered by tests

## PHASE 12 — DEPLOYMENT
- Objective
   - Prepare the platform for production deployment.

- Deliverables
   - Docker containers
   - Infrastructure
   - CI/CD

- Tasks
   - Containers
      - Backend Dockerfile
      - Streamlit Dockerfile
      - Docker Compose
   - Infrastructure
      - Kubernetes manifests
      - Terraform configuration
      - Nginx configuration
   - CI/CD
      - Linting
      - Testing
      - Build pipeline
      - Deployment pipeline
   - Monitoring
      - Logging
      - Metrics
      - Health checks
   - Definition of Done
      - Application deploys successfully using Docker Compose
      - CI pipeline passes
      - System health checks operational

## PHASE 13: POLISH
- Logging
- Error handling
- Type safety
- Documentation completion

---

# 🤖 AGENT DESIGN RULES

Each agent must:

- Have single responsibility
- Accept structured input only
- Return structured output only
- Never directly call other agents
- Operate only through LangGraph state

Agents:
- Weather Intelligence Agent
- Forecasting Agent
- Anomaly Detection Agent
- Root Cause Analysis Agent

---

# 🔄 LANGGRAPH RULES

- SystemState is the ONLY shared object
- Nodes must be deterministic where possible
- LLM calls only allowed in RCA and reporting
- Conditional branching allowed only via orchestrator
- HITL node must block execution when required

---

# 📊 DATA CONTRACT ENFORCEMENT

- All outputs MUST match data_schema.md exactly
- No extra fields allowed unless metadata
- All timestamps must be ISO-8601
- Null values must be explicit
- All outputs must be JSON serializable

---

# 🧪 QUALITY GATES (MANDATORY CHECKS)

Before completing any phase:

✔ Code runs without errors  
✔ Schema validation passes  
✔ No cross-layer logic leakage  
✔ Agent outputs are structured  
✔ API endpoints respond correctly  
✔ LangGraph flow executes end-to-end  

---

# 🚨 FAILURE HANDLING

If any component fails:
- Do NOT proceed to next phase
- Fix root cause first
- Ensure schema compliance
- Ensure modular integrity

---

# 🧠 FINAL OBJECTIVE

At completion, the repository must function as:

"A fully operational agentic AI system simulating a Solar Operations Control Center."

It must demonstrate:
- real ML forecasting
- anomaly detection
- LLM-based reasoning
- multi-agent orchestration
- human-in-the-loop governance
- production-grade architecture

---

# 🎯 SUCCESS CRITERIA

The system is complete when:

- A full daily solar operations report can be generated automatically
- Anomalies are detected and explained
- Root causes are generated using LLM reasoning
- Human approval workflow is functional
- Streamlit Frontend displays system state correctly
- Backend executes full LangGraph workflow end-to-end

---

BEGIN EXECUTION NOW. FOLLOW TASKS.MD STRICTLY.