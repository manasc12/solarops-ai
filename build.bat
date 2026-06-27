@echo off
REM SolarOps AI — Windows developer task runner.
REM Usage: build.bat <task>
REM Or:    build.bat help

setlocal enabledelayedexpansion
set PYTHONPATH=.

if "%1"=="" (
    call :show_help
    exit /b 0
)

if /i "%1"=="help" (
    call :show_help
    exit /b 0
) else if /i "%1"=="install" (
    call :invoke_install
    exit /b 0
) else if /i "%1"=="data" (
    call :invoke_data
    exit /b 0
) else if /i "%1"=="train" (
    call :invoke_train
    exit /b 0
) else if /i "%1"=="backend" (
    call :invoke_backend
    exit /b 0
) else if /i "%1"=="frontend" (
    call :invoke_frontend
    exit /b 0
) else if /i "%1"=="test" (
    call :invoke_test
    exit /b 0
) else if /i "%1"=="lint" (
    call :invoke_lint
    exit /b 0
) else if /i "%1"=="clean" (
    call :invoke_clean
    exit /b 0
) else if /i "%1"=="docker-up" (
    call :invoke_docker_up
    exit /b 0
) else if /i "%1"=="docker-down" (
    call :invoke_docker_down
    exit /b 0
) else (
    echo Unknown task: %1
    echo.
    call :show_help
    exit /b 1
)

:show_help
echo SolarOps AI - Developer Task Runner
echo.
echo Available tasks:
echo.
echo   help              Show this help message
echo   install           Install Python dependencies
echo   data              Seed farm registry and build the RAG index
echo   train             Train forecasting + anomaly models
echo   backend           Run the FastAPI backend (port 8000)
echo   frontend          Run the Streamlit console (port 8501)
echo   test              Run the test suite
echo   lint              Byte-compile check across the source tree
echo   clean             Remove caches and trained artifacts
echo   docker-up         Build and start the full stack via docker-compose
echo   docker-down       Stop the stack
echo.
echo Usage:
echo   build.bat backend
echo   build.bat data
echo.
exit /b 0

:invoke_install
echo Installing Python dependencies...
pip install -r requirements.txt
echo [OK] Dependencies installed
exit /b 0

:invoke_data
echo Seeding farm registry and building RAG index...
powershell -ExecutionPolicy Bypass -File scripts\load_data.ps1
echo [OK] Data seeded
exit /b 0

:invoke_train
echo Training forecasting + anomaly models...
powershell -ExecutionPolicy Bypass -File scripts\train_models.ps1
echo [OK] Models trained
exit /b 0

:invoke_backend
echo Starting FastAPI backend (port 8000)...
powershell -ExecutionPolicy Bypass -File scripts\run_backend.ps1
exit /b 0

:invoke_frontend
echo Starting Streamlit console (port 8501)...
powershell -ExecutionPolicy Bypass -File scripts\run_streamlit.ps1
exit /b 0

:invoke_test
echo Running test suite...
python -m pytest backend/tests -q
echo [OK] Tests completed
exit /b 0

:invoke_lint
echo Byte-compile check across source tree...
python -m compileall -q backend ml agents rag workflows streamlit_app
echo [OK] Lint check completed
exit /b 0

:invoke_clean
echo Cleaning caches and artifacts...
if exist .pytest_cache rmdir /s /q .pytest_cache >nul 2>&1
for /d /r . %%d in (__pycache__) do if exist "%%d" rmdir /s /q "%%d" >nul 2>&1
if exist data\processed\models rmdir /s /q data\processed\models >nul 2>&1
if exist data\processed\rag_index rmdir /s /q data\processed\rag_index >nul 2>&1
echo [OK] Cleanup completed
exit /b 0

:invoke_docker_up
echo Building and starting the full stack via docker-compose...
docker compose up --build
exit /b 0

:invoke_docker_down
echo Stopping the stack...
docker compose down
echo [OK] Stack stopped
exit /b 0
