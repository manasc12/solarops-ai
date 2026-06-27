"""Maintenance knowledge workflow.

Bridges operational RCA to grounded maintenance guidance: given a farm's latest
RCA, query the RAG knowledge base for recommended maintenance actions.

Run standalone:
    python -m workflows.maintenance_flow_graph FARM_002
"""

from __future__ import annotations

import sys

from backend.app.models.schemas import RAGQueryResult
from backend.app.services.rca_service import get_rca_service
from rag.generation.rag_chain import get_rag_chain


def run_maintenance_flow(farm_id: str) -> RAGQueryResult: #TODO: deadcode, this function has not been used anywhere in the project! It has been used in this file only!
    rca = get_rca_service().analyze(farm_id)
    top_cause = rca.root_causes[0] if rca.root_causes else "equipment underperformance"
    query = f"Recommended maintenance actions for: {top_cause}"
    return get_rag_chain().answer(query)


if __name__ == "__main__":
    farm = sys.argv[1] if len(sys.argv) > 1 else "FARM_002"
    result = run_maintenance_flow(farm)
    print("Q:", result.query)
    print("A:", result.answer)
