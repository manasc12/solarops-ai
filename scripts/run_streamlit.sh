#!/usr/bin/env bash
# Launch the SolarOps Streamlit operations console.
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-.}"

PORT="${STREAMLIT_PORT:-8501}"
export BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

exec python -m streamlit run streamlit_app/app.py \
  --server.port "$PORT" \
  --server.address "0.0.0.0"
