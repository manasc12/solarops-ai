#!/usr/bin/env bash
# Train and persist the ML artifacts (forecasting + anomaly detection).
# Artifacts are written to data/processed/models/ and reused at inference time.
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-.}"

echo "[train] forecasting model (LightGBM)…"
python -m ml.training.train_forecasting

echo "[train] anomaly detector (IsolationForest)…"
python -m ml.training.train_anomaly

echo "[train] done. Artifacts in data/processed/models/"
