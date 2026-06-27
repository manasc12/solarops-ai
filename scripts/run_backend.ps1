# Launch the SolarOps FastAPI backend.
# The repo root is placed on PYTHONPATH so the package tree imports cleanly.

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptDir\.."

$env:PYTHONPATH = "$PWD"
$host_env = $env:API_HOST
$port_env = $env:API_PORT

$HOST = if ($host_env) { $host_env } else { "0.0.0.0" }
$PORT = if ($port_env) { $port_env } else { "8000" }

Write-Host "Starting FastAPI backend on $HOST`:$PORT…"
python -m uvicorn backend.app.main:app --host $HOST --port $PORT --reload
