#!/usr/bin/env bash
# Warm the data layer: seed the farm registry and build the RAG knowledge index.
# Farm metadata is loaded from configs/app_config.yaml; the RAG index is built
# from the maintenance manuals under rag/data/manuals/.
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-.}"

echo "[data] seeding farm registry…"
python -c "from backend.app.db.repository import FarmRepository; print('farms:', [f.farm_id for f in FarmRepository().list()])"

echo "[data] building RAG maintenance index…"
python -c "from rag.retrieval.retriever import get_retriever; print('indexed chunks:', get_retriever().ensure_index())"

echo "[data] done."
