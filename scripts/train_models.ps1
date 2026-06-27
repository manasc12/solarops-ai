# Train and persist the ML artifacts (forecasting + anomaly detection).
# Artifacts are written to data/processed/models/ and reused at inference time.

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptDir\.."

$env:PYTHONPATH = "$PWD"

Write-Host "[train] forecasting model (LightGBM)…"
python -m ml.training.train_forecasting

Write-Host "[train] anomaly detector (IsolationForest)…"
python -m ml.training.train_anomaly

Write-Host "[train] done. Artifacts in data/processed/models/"
