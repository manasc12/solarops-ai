# SolarOps AI — Windows developer task runner.
# Usage: .\build.ps1 <task>
# Or:    .\build.ps1 help

param(
    [string]$Task = "help"
)

$ErrorActionPreference = "Stop"

# Set PYTHONPATH
$env:PYTHONPATH = "."

function Show-Help {
    Write-Host "SolarOps AI — Developer Task Runner" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Available tasks:" -ForegroundColor Green
    Write-Host ""
    Write-Host "  help              Show this help message"
    Write-Host "  install           Install Python dependencies"
    Write-Host "  data              Seed farm registry and build the RAG index"
    Write-Host "  train             Train forecasting + anomaly models"
    Write-Host "  backend           Run the FastAPI backend (port 8000)"
    Write-Host "  frontend          Run the Streamlit console (port 8501)"
    Write-Host "  test              Run the test suite"
    Write-Host "  lint              Byte-compile check across the source tree"
    Write-Host "  clean             Remove caches and trained artifacts"
    Write-Host "  docker-up         Build and start the full stack via docker-compose"
    Write-Host "  docker-down       Stop the stack"
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\build.ps1 backend          # Run backend"
    Write-Host "  .\build.ps1 data             # Load data"
    Write-Host ""
}

function Invoke-Install {
    Write-Host "Installing Python dependencies…" -ForegroundColor Cyan
    pip install -r requirements.txt
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
}

function Invoke-Data {
    Write-Host "Seeding farm registry and building RAG index…" -ForegroundColor Cyan
    & .\scripts\load_data.ps1
    Write-Host "✓ Data seeded" -ForegroundColor Green
}

function Invoke-Train {
    Write-Host "Training forecasting + anomaly models…" -ForegroundColor Cyan
    & .\scripts\train_models.ps1
    Write-Host "✓ Models trained" -ForegroundColor Green
}

function Invoke-Backend {
    Write-Host "Starting FastAPI backend (port 8000)…" -ForegroundColor Cyan
    & .\scripts\run_backend.ps1
}

function Invoke-Frontend {
    Write-Host "Starting Streamlit console (port 8501)…" -ForegroundColor Cyan
    & .\scripts\run_streamlit.ps1
}

function Invoke-Test {
    Write-Host "Running test suite…" -ForegroundColor Cyan
    python -m pytest backend/tests -q
    Write-Host "✓ Tests completed" -ForegroundColor Green
}

function Invoke-Lint {
    Write-Host "Byte-compile check across source tree…" -ForegroundColor Cyan
    python -m compileall -q backend ml agents rag workflows streamlit_app
    Write-Host "✓ Lint check completed" -ForegroundColor Green
}

function Invoke-Clean {
    Write-Host "Cleaning caches and artifacts…" -ForegroundColor Cyan
    
    if (Test-Path ".pytest_cache") {
        Remove-Item -Recurse -Force .pytest_cache -ErrorAction SilentlyContinue
    }
    
    Get-ChildItem -Recurse -Filter "__pycache__" -Directory | Remove-Item -Recurse -Force
    
    if (Test-Path "data/processed/models") {
        Remove-Item -Recurse -Force "data/processed/models/*" -ErrorAction SilentlyContinue
    }
    
    if (Test-Path "data/processed/rag_index") {
        Remove-Item -Recurse -Force "data/processed/rag_index/*" -ErrorAction SilentlyContinue
    }
    
    Write-Host "✓ Cleanup completed" -ForegroundColor Green
}

function Invoke-DockerUp {
    Write-Host "Building and starting the full stack via docker-compose…" -ForegroundColor Cyan
    docker compose up --build
}

function Invoke-DockerDown {
    Write-Host "Stopping the stack…" -ForegroundColor Cyan
    docker compose down
    Write-Host "✓ Stack stopped" -ForegroundColor Green
}

# Route to task
switch ($Task.ToLower()) {
    "help" { Show-Help }
    "install" { Invoke-Install }
    "data" { Invoke-Data }
    "train" { Invoke-Train }
    "backend" { Invoke-Backend }
    "frontend" { Invoke-Frontend }
    "test" { Invoke-Test }
    "lint" { Invoke-Lint }
    "clean" { Invoke-Clean }
    "docker-up" { Invoke-DockerUp }
    "docker-down" { Invoke-DockerDown }
    default {
        Write-Host "Unknown task: $Task" -ForegroundColor Red
        Write-Host ""
        Show-Help
        exit 1
    }
}
