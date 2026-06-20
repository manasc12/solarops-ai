#!/usr/bin/env bash
# Launch the SolarOps FastAPI backend.
# The repo root is placed on PYTHONPATH so the package tree imports cleanly.
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-.}"

HOST="${API_HOST:-0.0.0.0}"
PORT="${API_PORT:-8000}"

exec python -m uvicorn backend.app.main:app --host "$HOST" --port "$PORT"
