# SolarOps AI – Execution Plan (TASKS.md)

## Purpose

This document defines the **strict execution order** for building the SolarOps AI system.

It ensures:
- deterministic build sequence
- dependency-safe implementation
- incremental system validation
- agentic AI components are built only after foundational systems exist

This is NOT a feature list.

It is a **build orchestration blueprint**.

---

# ⚠️ Execution Rules (STRICT)

- Do NOT skip steps
- Do NOT implement advanced components before foundations
- Each task must be completed and verified before moving forward
- Prefer simple working implementations first
- No overengineering in early phases
- Every module must be runnable independently

---

# 🧱 PHASE 0 — PROJECT BOOTSTRAP

## TASK 0.1 — Repository Initialization
- Create folder structure as defined in architecture.md
- Initialize Python backend (FastAPI)
- Initialize Streamlit frontend
- Add base configuration files:
  - pyproject.toml
  - .env.example
  - docker-compose.yml
  - README.md (minimal)

✔ Output:
Clean repository skeleton with no business logic

---

## TASK 0.2 — Core Tooling Setup
- Configure linting (ruff / black)
- Add type checking (mypy optional)
- Add logging utility (structured logging)
- Setup base FastAPI app entrypoint

✔ Output:
Backend runs with `/health` endpoint

---

# 🌤 PHASE 1 — DATA FOUNDATION

## TASK 1.1 — Weather API Integration
- Implement Open-Meteo service
- Implement NASA POWER service (mock allowed)
- Normalize outputs into unified schema

✔ Output:
Weather service returns structured JSON

---

## TASK 1.2 — Data Schema Definition
- Define Pydantic models:
  - WeatherData
  - FarmMetadata
  - EnergyObservation

✔ Output:
Central schema file used across system

---

## TASK 1.3 — Mock SCADA Data Generator
- Simulate solar farm sensor data
- Include:
  - energy output
  - temperature
  - inverter status

✔ Output:
Synthetic time-series dataset

---

# 📈 PHASE 2 — MACHINE LEARNING LAYER

## TASK 2.1 — Feature Engineering Pipeline
- Create reusable feature generator:
  - time features
  - weather features
  - lag features

✔ Output:
Feature matrix ready for ML

---

## TASK 2.2 — Forecasting Model (Baseline)
- Train LightGBM model
- Predict daily solar output
- Save model artifact locally

✔ Output:
Working forecast pipeline

---

## TASK 2.3 — Forecast Inference Service
- Wrap ML model into service
- Provide API-compatible output

✔ Output:
`forecast_service.py` returns predictions

---

# 🚨 PHASE 3 — ANOMALY DETECTION

## TASK 3.1 — Anomaly Detection Model
- Implement Isolation Forest
- Detect deviation between:
  - predicted vs actual output

✔ Output:
Anomaly score per farm

---

## TASK 3.2 — Anomaly Service Layer
- Expose anomaly detection via backend service
- Define severity levels:
  - LOW
  - MEDIUM
  - HIGH

✔ Output:
Structured anomaly response

---

# 🤖 PHASE 4 — AGENTIC LAYER (CORE SYSTEM)

## TASK 4.1 — Weather Agent
- Wrap weather service into agent module
- Output structured operational insights

---

## TASK 4.2 — Forecast Agent
- Integrate ML forecasting into agent
- Add reasoning layer (LLM optional)

---

## TASK 4.3 — Anomaly Agent
- Convert anomaly output into agent reasoning step

---

## TASK 4.4 — Root Cause Analysis Agent (RCA)
- Implement LLM-based explanation system
- Input:
  - anomaly
  - weather context
  - forecast deviation

✔ Output:
Human-readable root cause explanation

---

# 🧠 PHASE 5 — LANGGRAPH ORCHESTRATION

## TASK 5.1 — State Definition
- Define global system state object
- Ensure all agents use shared schema

---

## TASK 5.2 — Graph Construction
- Build LangGraph pipeline:

Weather → Forecast → Anomaly → (RCA if needed) → Report

---

## TASK 5.3 — Conditional Routing
- If anomaly_score > threshold:
  - trigger RCA node
- Else skip RCA

---

## TASK 5.4 — Report Generator Node
- Generate daily operations summary
- Include:
  - production forecast
  - risk summary
  - anomalies
  - recommendations

---

# 🔍 PHASE 6 — RAG SYSTEM (KNOWLEDGE LAYER)

## TASK 6.1 — Document Ingestion
- Load maintenance manuals (PDF/text)
- Chunk documents

---

## TASK 6.2 — Embedding Pipeline
- Generate embeddings
- Store in vector DB (FAISS or Chroma)

---

## TASK 6.3 — Retrieval + QA Chain
- Implement semantic search
- Build RAG response generator

✔ Output:
Maintenance Q&A system

---

# 👨‍💼 PHASE 7 — HUMAN-IN-THE-LOOP (HITL)

## TASK 7.1 — Approval System Design
- Define approval states:
  - PENDING
  - APPROVED
  - REJECTED

---

## TASK 7.2 — Backend API
- Implement endpoints:
  - submit approval request
  - approve/reject action
  - fetch pending approvals

---

## TASK 7.3 — Integration with LangGraph
- Block execution on HIGH severity anomalies
- Require approval before proceeding

---

# 🌐 PHASE 8 — STREAMLIT FRONTEND DASHBOARD

## TASK 8.1 — Dashboard UI
- Create main dashboard:
  - farm overview
  - production charts
  - anomaly alerts

---

## TASK 8.2 — RCA Viewer
- Display root cause explanations clearly

---

## TASK 8.3 — Approval Panel
- Show pending HITL actions
- Allow approve/reject

---

# 🔗 PHASE 9 — END-TO-END INTEGRATION

## TASK 9.1 — Full Pipeline Test
Simulate:
User request → API → LangGraph → ML → RCA → UI

---

## TASK 9.2 — Data Flow Validation
Ensure:
- No schema violations
- No missing fields
- No unhandled nulls

---

## TASK 9.3 — System Debugging Pass
- Fix integration issues
- Align agent outputs
- Standardize responses

---

# 📊 PHASE 10 — POLISH & PRODUCTION READINESS

## TASK 10.1 — Logging & Observability
- Add structured logs per agent
- Track execution flow

---

## TASK 10.2 — Code Cleanup
- Remove duplication
- Enforce type hints
- Improve naming consistency

---

## TASK 10.3 — Documentation Finalization
- Complete README.md
- Add architecture diagrams
- Add system walkthrough

---

# 🧠 FINAL SYSTEM CHECK

System is complete when:

✔ All agents work independently  
✔ LangGraph orchestrates full workflow  
✔ RAG system responds correctly  
✔ HITL blocks critical actions  
✔ Dashboard reflects real-time state  
✔ End-to-end pipeline runs without manual intervention  

---

# 🚀 END GOAL

A fully functional **Agentic Renewable Energy Operations System** demonstrating:

- AI agents
- ML forecasting
- anomaly detection
- reasoning (RCA)
- RAG knowledge system
- human-in-the-loop governance
- production-style architecture