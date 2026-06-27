# SolarOps AI — Developer Task Runner Guide

Complete guide to running SolarOps AI development tasks using the Makefile (Unix/Linux/Mac) or PowerShell task runner (Windows).

## Table of Contents

1. [Quick Start](#quick-start)
2. [Makefile (Unix/Linux/Mac)](#makefile-unixlinuxmac)
3. [PowerShell Runner (Windows)](#powershell-runner-windows)
4. [Batch Runner (Windows Alternative)](#batch-runner-windows-alternative)
5. [Common Workflows](#common-workflows)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### On Linux/Mac (Using Makefile)
```bash
# Show available tasks
make help

# Install dependencies
make install

# Load data and initialize database
make data

# Start backend
make backend

# Start frontend (in another terminal)
make frontend

# Train models
make train
```

### On Windows (Using PowerShell)
```powershell
# Show available tasks
.\build.ps1 help

# Install dependencies
.\build.ps1 install

# Load data and initialize database
.\build.ps1 data

# Start backend
.\build.ps1 backend

# Start frontend (in another terminal)
.\build.ps1 frontend

# Train models
.\build.ps1 train
```

### On Windows (Using Batch File)
```batch
# Show available tasks
.\build.bat help

# Install dependencies
.\build.bat install

# Load data and initialize database
.\build.bat data

# Start backend
.\build.bat backend
```

---

## Makefile (Unix/Linux/Mac)

### Overview

The `Makefile` is a task automation tool for Unix-based systems. It provides convenient shortcuts for common development tasks.

### Installation

The Makefile comes pre-configured. No additional setup needed—just run `make` commands.

### Available Tasks

| Task | Command | Description |
|------|---------|-------------|
| Help | `make help` | Show all available tasks |
| Install | `make install` | Install Python dependencies from `requirements.txt` |
| Data | `make data` | Seed farm registry and build RAG index |
| Train | `make train` | Train forecasting + anomaly detection models |
| Backend | `make backend` | Run FastAPI backend on port 8000 |
| Frontend | `make frontend` | Run Streamlit console on port 8501 |
| Test | `make test` | Run pytest test suite |
| Lint | `make lint` | Byte-compile check (syntax validation) |
| Clean | `make clean` | Remove caches, test artifacts, and trained models |
| Docker Up | `make docker-up` | Build and start Docker Compose stack |
| Docker Down | `make docker-down` | Stop Docker Compose stack |

### Usage Examples

```bash
# Initialize development environment
make install
make data

# Run backend in terminal 1
make backend

# Run frontend in terminal 2
make frontend

# Run tests
make test

# Check code syntax
make lint

# Clean up
make clean
```

### How It Works

- **PYTHONPATH:** Automatically set to `.` (repo root)
- **Script runner:** Calls bash scripts in `scripts/` directory
- **Python execution:** Uses `python` command (requires virtual environment to be activated)

---

## PowerShell Runner (Windows)

### Overview

`build.ps1` is a modern PowerShell task runner that replaces the Unix Makefile for Windows developers.

### Installation

No installation needed—just run from the project root:

```powershell
.\build.ps1 help
```

### Prerequisites

- **PowerShell 5.0+** (built into Windows 10+)
- **Python virtual environment activated** (`.venv\Scripts\Activate.ps1`)

### Available Tasks

| Task | Command | Description |
|------|---------|-------------|
| Help | `.\build.ps1 help` | Show all available tasks |
| Install | `.\build.ps1 install` | Install Python dependencies |
| Data | `.\build.ps1 data` | Seed farms + build RAG index + init database |
| Train | `.\build.ps1 train` | Train forecasting + anomaly models |
| Backend | `.\build.ps1 backend` | Start FastAPI backend (port 8000) |
| Frontend | `.\build.ps1 frontend` | Start Streamlit console (port 8501) |
| Test | `.\build.ps1 test` | Run pytest test suite |
| Lint | `.\build.ps1 lint` | Byte-compile check (syntax validation) |
| Clean | `.\build.ps1 clean` | Remove caches and artifacts |
| Docker Up | `.\build.ps1 docker-up` | Start Docker Compose stack |
| Docker Down | `.\build.ps1 docker-down` | Stop Docker Compose stack |

### Usage Examples

```powershell
# Initialize development environment
.\build.ps1 install
.\build.ps1 data

# Run backend in terminal 1
.\build.ps1 backend

# Run frontend in terminal 2
.\build.ps1 frontend

# Run tests
.\build.ps1 test

# Check code syntax
.\build.ps1 lint

# Clean up
.\build.ps1 clean
```

### Features

✅ **Colored Output** — Status messages color-coded for readability  
✅ **Error Handling** — Stops on first error with clear messages  
✅ **Cross-Platform** — Works on Windows, PowerShell Core on Mac/Linux  
✅ **Auto PYTHONPATH** — Sets environment variables automatically  
✅ **User-Friendly** — Progress indicators and success messages  

### Execution Policy

If you get an error about execution policy:

```powershell
# Allow running scripts for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then run
.\build.ps1 help
```

---

## Batch Runner (Windows Alternative)

### Overview

`build.bat` is a traditional Windows batch file alternative for environments where PowerShell isn't available.

### Usage

```batch
.\build.bat help
.\build.bat backend
.\build.bat frontend
.\build.bat data
```

### Limitations

- ⚠️ No colored output
- ⚠️ Less readable error messages
- ⚠️ Older syntax
- ✅ Maximum compatibility with legacy Windows systems

**Recommendation:** Use `build.ps1` unless you have compatibility issues.

---

## Common Workflows

### Workflow 1: Full Cold Start (From Scratch)

Start with a fresh clone or after cleaning everything.

**Unix/Mac:**
```bash
make install
make data
make train
make backend
```

**Windows (PowerShell):**
```powershell
.\build.ps1 install
.\build.ps1 data
.\build.ps1 train
.\build.ps1 backend
```

**What happens:**
1. Installs all dependencies
2. Initializes SQLite database + loads 3 farms
3. Trains forecasting + anomaly models
4. Starts backend API on port 8000

### Workflow 2: Development Session

For active development with both backend and frontend.

**Unix/Mac (Terminal 1):**
```bash
make backend
```

**Unix/Mac (Terminal 2):**
```bash
make frontend
```

**Windows PowerShell (Terminal 1):**
```powershell
.\build.ps1 backend
```

**Windows PowerShell (Terminal 2):**
```powershell
.\build.ps1 frontend
```

**Access:**
- Backend API: http://localhost:8000
- Backend Docs: http://localhost:8000/docs
- Frontend: http://localhost:8501

### Workflow 3: Testing & Validation

```bash
# Unix/Mac
make lint
make test

# Windows
.\build.ps1 lint
.\build.ps1 test
```

### Workflow 4: Clean & Rebuild

```bash
# Unix/Mac
make clean
make train

# Windows
.\build.ps1 clean
.\build.ps1 train
```

### Workflow 5: Docker Deployment

```bash
# Unix/Mac
make docker-up
make docker-down

# Windows
.\build.ps1 docker-up
.\build.ps1 docker-down
```

---

## Port Reference

| Service | Default Port | Used By |
|---------|--------------|---------|
| FastAPI Backend | 8000 | REST API, docs (http://localhost:8000/docs) |
| Streamlit Frontend | 8501 | Web UI (http://localhost:8501) |
| PostgreSQL* | 5432 | Database (Docker only) |
| Redis* | 6379 | Cache (Docker only) |

*Docker containers only

---

## Environment Variables

Both task runners support environment variables for customization:

### Backend
```bash
# Unix/Mac
export API_HOST="0.0.0.0"
export API_PORT="8000"
make backend

# Windows (PowerShell)
$env:API_HOST = "0.0.0.0"
$env:API_PORT = "8000"
.\build.ps1 backend
```

### Frontend
```bash
# Unix/Mac
export BACKEND_URL="http://localhost:8000"
export STREAMLIT_PORT="8501"
make frontend

# Windows (PowerShell)
$env:BACKEND_URL = "http://localhost:8000"
$env:STREAMLIT_PORT = "8501"
.\build.ps1 frontend
```

---

## File Locations

| Component | Path | Purpose |
|-----------|------|---------|
| Backend code | `backend/` | FastAPI application |
| Frontend code | `streamlit_app/` | Streamlit UI |
| ML models | `ml/` | Training + inference |
| Agents | `agents/` | LangGraph orchestration |
| Database | `data/solarops.db` | SQLite database |
| Configs | `configs/` | Application configuration |
| Scripts | `scripts/` | Bash/PowerShell automation |
| Tests | `backend/tests/` | Test suite |

---

## Troubleshooting

### Issue: "make: command not found" on Windows

**Solution:** Use PowerShell instead
```powershell
.\build.ps1 help
```

### Issue: Python module not found errors

**Solution:** Ensure dependencies are installed
```bash
# Unix/Mac
make install

# Windows
.\build.ps1 install
```

### Issue: "Permission denied" when running scripts on Mac/Linux

**Solution:** Make scripts executable
```bash
chmod +x scripts/*.sh
make backend
```

### Issue: Port already in use

**Solution:** Change the port via environment variable

```bash
# Unix/Mac
export API_PORT="8001"
make backend

# Windows
$env:API_PORT = "8001"
.\build.ps1 backend
```

### Issue: Cannot execute script (PowerShell execution policy)

**Solution:** Update execution policy
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\build.ps1 help
```

### Issue: Database not found on first run

**Solution:** Run data initialization
```bash
# Unix/Mac
make data

# Windows
.\build.ps1 data
```

This will:
- Create `data/solarops.db`
- Initialize all tables
- Load 3 farms from config
- Build RAG index

---

## Development Best Practices

### ✅ DO

- Use the task runner for common tasks (consistency)
- Run `make lint` or `.\build.ps1 lint` before committing
- Run tests with `make test` or `.\build.ps1 test` regularly
- Keep dependencies updated: `make install` or `.\build.ps1 install`
- Clean artifacts before long builds: `make clean` or `.\build.ps1 clean`

### ❌ DON'T

- Don't run Python scripts directly—use the task runner
- Don't modify `PYTHONPATH` manually (runner handles it)
- Don't mix Unix Makefile with PowerShell scripts
- Don't commit generated files (`.pytest_cache`, `__pycache__`, models)
- Don't skip the `lint` step before pushing

---

## Quick Reference Card

```bash
# Show all tasks
make help                    # Unix/Mac
.\build.ps1 help            # Windows

# Setup
make install                 # Unix/Mac
.\build.ps1 install         # Windows

# Initialize database
make data                    # Unix/Mac
.\build.ps1 data            # Windows

# Run services
make backend                 # Unix/Mac → API on :8000
make frontend                # Unix/Mac → UI on :8501

.\build.ps1 backend         # Windows → API on :8000
.\build.ps1 frontend        # Windows → UI on :8501

# Quality
make lint                    # Unix/Mac
make test                    # Unix/Mac

.\build.ps1 lint            # Windows
.\build.ps1 test            # Windows

# Cleanup
make clean                   # Unix/Mac
.\build.ps1 clean           # Windows
```

---

## Support

For issues or questions:

1. Check the **Troubleshooting** section above
2. Review `.github/ARCHITECTURE.md` for system design
3. Check `.github/TECH_STACK.md` for dependencies
4. Review `.github/copilot-instructions.md` for coding standards
5. Open an issue with task runner output and error logs

---

## Summary

| OS | Task Runner | Command |
|----|-------------|---------|
| Linux/Mac | Makefile | `make <task>` |
| Windows (Modern) | PowerShell | `.\build.ps1 <task>` |
| Windows (Legacy) | Batch | `.\build.bat <task>` |

**All runners support the same tasks and maintain feature parity.** Choose based on your OS and preferences!
