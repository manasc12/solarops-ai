# Windows Task Runner Guide

SolarOps AI now has two Windows alternatives to the Unix Makefile:

## 1. PowerShell Version (Recommended)

**File:** `build.ps1`

```powershell
# Show help
.\build.ps1 help

# Common tasks
.\build.ps1 backend      # Start FastAPI backend
.\build.ps1 frontend     # Start Streamlit
.\build.ps1 data         # Load database + farms + RAG index
.\build.ps1 train        # Train ML models
.\build.ps1 test         # Run tests
.\build.ps1 clean        # Clean caches and artifacts
.\build.ps1 install      # Install dependencies
.\build.ps1 lint         # Check syntax
.\build.ps1 docker-up    # Start Docker stack
.\build.ps1 docker-down  # Stop Docker stack
```

**Advantages:**
- ✅ Modern, readable syntax
- ✅ Colored output
- ✅ Better error handling
- ✅ Cross-platform compatible
- ✅ Part of PowerShell ecosystem

## 2. Batch File Version (Alternative)

**File:** `build.bat`

```batch
REM Show help
build.bat help

REM Common tasks
.\build.bat backend      # Start FastAPI backend
.\build.bat frontend     # Start Streamlit
.\build.bat data         # Load database + farms + RAG index
.\build.bat train        # Train ML models
.\build.bat test         # Run tests
.\build.bat clean        # Clean caches and artifacts
.\build.bat install      # Install dependencies
.\build.bat lint         # Check syntax
.\build.bat docker-up    # Start Docker stack
.\build.bat docker-down  # Stop Docker stack
```

**Advantages:**
- ✅ Compatible with older Windows systems
- ✅ No PowerShell required
- ✅ Native CMD.EXE support
- ✅ Lightweight

## Quick Start

### Option A: Use PowerShell
```powershell
# Terminal 1: Start backend
.\build.ps1 backend

# Terminal 2: Start frontend
.\build.ps1 frontend

# Terminal 3: Load data
.\build.ps1 data
```

### Option B: Use Batch
```batch
REM Terminal 1: Start backend
.\build.bat backend

REM Terminal 2: Start frontend
.\build.bat frontend

REM Terminal 3: Load data
.\build.bat data
```

## Comparison

| Feature | Unix Makefile | PowerShell (build.ps1) | Batch (build.bat) |
|---------|--------------|----------------------|------------------|
| Works on Windows | ❌ | ✅ | ✅ |
| Readable output | ✅ | ✅ | ✅ |
| Color support | ✅ | ✅ | Limited |
| Modern syntax | ✅ | ✅ | ❌ |
| Lightweight | ✅ | ✅ | ✅ |
| PowerShell required | ❌ | ✅ | ❌ |

## Which Should I Use?

- **For most developers:** Use `build.ps1` (PowerShell) - modern, maintainable, cleaner output
- **For legacy systems:** Use `build.bat` (Batch file) - more compatible
- **For CI/CD pipelines:** Use either, both work reliably
- **For automation:** PowerShell is preferred for new projects

## All Tasks Reference

| Task | Description |
|------|-------------|
| `help` | Show this help message |
| `install` | Install Python dependencies from requirements.txt |
| `data` | Initialize database, seed farms, build RAG index |
| `train` | Train forecasting + anomaly detection models |
| `backend` | Start FastAPI backend on port 8000 |
| `frontend` | Start Streamlit console on port 8501 |
| `test` | Run pytest test suite |
| `lint` | Byte-compile check (syntax validation) |
| `clean` | Remove __pycache__, .pytest_cache, trained models |
| `docker-up` | Build and start Docker Compose stack |
| `docker-down` | Stop Docker Compose stack |

## Troubleshooting

### PowerShell: "cannot be loaded because running scripts is disabled"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Batch: Command not found
Use full path:
```batch
.\build.bat backend
```

## Notes

- Both task runners set `PYTHONPATH=.` automatically
- All tasks run from the project root directory
- Backend runs on `0.0.0.0:8000`
- Frontend runs on `0.0.0.0:8501`
