# Warm the data layer: seed the farm registry and build the RAG knowledge index.
# Farm metadata is loaded from configs/app_config.yaml; the RAG index is built
# from the maintenance manuals under rag/data/manuals/.

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptDir\.."

Write-Host "[data] initializing database…"
python -c "from backend.app.db.session import init_db; init_db(); print('✓ Database initialized')"

Write-Host "[data] seeding farm registry…"
python -c "from backend.app.db.repository import FarmRepository; farms = FarmRepository().list(); print(f'✓ Loaded {len(farms)} farms:', [f.farm_id for f in farms])"

Write-Host "[data] building RAG maintenance index…"
python -c "from rag.retrieval.retriever import get_retriever; chunks = get_retriever().ensure_index(); print(f'✓ Indexed {chunks} chunks')"

Write-Host "[data] done."
