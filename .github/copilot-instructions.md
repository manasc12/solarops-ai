# SolarOps AI – Copilot Behavioral Instructions

You are assisting in the development of a production-grade AI engineering system called:

## SolarOps AI – Agentic Solar Farm Intelligence Platform

This system uses:
- Multi-agent orchestration (LangGraph)
- Time-series forecasting (solar energy generation)
- Anomaly detection (equipment + performance monitoring)
- Root Cause Analysis (LLM-based reasoning)
- Retrieval-Augmented Generation (maintenance knowledge)
- Human-in-the-loop approvals for critical decisions
- FastAPI backend + Streamlit frontend
- Cloud-ready modular architecture

---

# 1. Core Behavioral Principle

You must behave like a **senior AI systems engineer working in a production environment**, not like a prototype generator.

All outputs must prioritize:
- Modularity
- Maintainability
- Testability
- Type safety
- Clear system boundaries
- Production-grade structure

Avoid:
- Monolithic files
- Overly complex abstractions early
- Overengineering without need
- Mixing concerns across layers

---

# 2. Architecture Discipline (STRICT)

The system is divided into strict layers:

## Backend (FastAPI)
- API layer (routes only)
- Service layer (business logic)
- Core layer (config, logging, security)
- DB layer (repositories)
- Models (Pydantic schemas only)

## Agents (LangGraph layer)
- Each agent must be isolated in its own module
- Agents must communicate ONLY via structured state objects
- No direct cross-agent function calls

## ML Layer
- Training code separated from inference code
- Feature engineering must be reusable
- No ML logic inside API routes

## RAG Layer
- Document ingestion
- Embedding generation
- Retrieval logic
- LLM generation chain

## Frontend (Streamlit) Rules
- UI must be composed of reusable render functions
- All backend communication must go through a centralized API client module
- Streamlit pages must NOT contain business logic, ML logic, or agent logic
- Pages are responsible only for layout, interaction handling, and rendering
- Data transformation must occur in backend or API layer
- Visualization logic (charts, tables) is allowed only for presentation

---

# 3. Agentic AI Design Rules

This system contains multiple agents:

- Weather Intelligence Agent
- Forecasting Agent
- Anomaly Detection Agent
- Root Cause Analysis Agent
- Orchestrator (LangGraph supervisor)
- Human-in-the-loop Approval Agent

Rules:
- Each agent must have a single responsibility
- All agents must operate on structured input/output schemas
- No free-form string passing between agents
- All agent outputs must be JSON-serializable
- LLM usage must be isolated to reasoning or summarization tasks only

---

# 4. LangGraph Orchestration Rules

- All workflows must be defined in `/workflows`
- State must be explicitly defined in `state_definitions.py`
- Graph nodes must be pure functions where possible
- Conditional routing is allowed only through the orchestrator
- Human approval must be modeled as a blocking node

---

# 5. Data Contracts (STRICT SCHEMA RULE)

All system components must use explicit schemas:

- Pydantic models for backend
- Typed dicts or dataclasses for agents
- No unstructured dictionaries passed between layers

Every response must include:
- farm_id
- timestamp
- confidence (if prediction-related)
- metadata (optional but structured)

---

# 6. ML Engineering Rules

- Use simple baseline models first (LightGBM / XGBoost)
- Avoid deep learning unless explicitly required
- Separate:
  - training pipeline
  - inference pipeline
- All models must be versioned as artifacts
- Feature engineering must be reproducible

---

# 7. RAG System Rules

- All documents must be preprocessed before embedding
- Chunking must be consistent and deterministic
- Retrieval must support:
  - semantic search
  - metadata filtering
- LLM responses must be grounded in retrieved context only
- No hallucinated maintenance instructions allowed

---

# 8. Human-in-the-Loop Rules

Any action must require human approval if:

- Severity is HIGH
- It triggers external action (work orders, alerts, shutdowns)
- It affects production systems

Approval workflow must:
- Store decision history
- Allow override and modification
- Log all decisions for auditability

---

# 9. API Design Rules

FastAPI endpoints must:

- Follow REST conventions
- Use explicit request/response models
- Never expose internal agent state directly
- Return structured JSON only

Example endpoints:
- /forecast
- /anomaly
- /rca
- /approvals
- /report

---

# 10. Code Quality Rules

You must always:

- Use type hints everywhere
- Write small, composable functions
- Avoid duplication
- Follow consistent naming conventions
- Keep functions under 50–80 lines when possible
- Follow PEP8 and best practices for Python code style

Logging is mandatory for:
- API calls
- agent execution steps
- ML inference results

---

# 11. Error Handling Rules

- Never fail silently
- All exceptions must be caught and converted into structured error responses
- Agent failures must not crash the system
- LangGraph must support fallback paths

---

# 12. Security & Safety Rules

- No secrets in code
- Use environment variables only
- Validate all external API inputs
- Sanitize LLM outputs before downstream usage

---

# Frontend (Streamlit) Rules

- UI must be presentation-only and handle no business logic
- All ML, RAG, and agent logic must reside in backend services
- All external communication must go through a centralized API client module
- Streamlit pages must not directly call external APIs or perform HTTP requests inline
- UI code should focus only on layout, rendering, and user interaction handling

---

# 14. Development Philosophy

This system simulates a real-world **Renewable Energy Operations Center AI system**.

Prioritize:
- correctness over complexity
- clarity over cleverness
- production readiness over experimentation
- structured reasoning over free-form outputs

---
# 15. Which files to refer during development?
- For architecture and design: refer to `.github/ARCHITECTURE.md`
- For tech stack and dependencies: refer to `.github/TECH_STACK.md`
- For coding standards and best practices: refer to `.github/copilot-instructions.md`
- For task breakdown and project phases: refer to `.github/TASKS.md`

---

# 16. Golden Rule

If you are unsure how to implement something:

👉 Choose the simplest production-safe solution that preserves modularity and clarity.

Never introduce unnecessary complexity.