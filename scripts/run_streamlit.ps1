# Launch the SolarOps Streamlit operations console.

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptDir\.."

$env:PYTHONPATH = "$PWD"
$port_env = $env:STREAMLIT_PORT
$backend_url_env = $env:BACKEND_URL

$PORT = if ($port_env) { $port_env } else { "8501" }
$BACKEND_URL = if ($backend_url_env) { $backend_url_env } else { "http://localhost:8000" }

$env:BACKEND_URL = $BACKEND_URL

Write-Host "Starting Streamlit frontend on port $PORT…"
Write-Host "Backend URL: $BACKEND_URL"
python -m streamlit run streamlit_app/app.py `
  --server.port $PORT `
  --server.address "0.0.0.0"
