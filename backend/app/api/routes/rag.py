"""RAG knowledge endpoints. Routes only — logic lives in the RAG chain."""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.models.requests import RAGQueryRequest
from backend.app.models.responses import APIResponse
from rag.generation.rag_chain import get_rag_chain

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/query", response_model=APIResponse)
def query_knowledge(req: RAGQueryRequest) -> APIResponse:
    result = get_rag_chain().answer(req.query, top_k=req.top_k)
    # Avoid returning bulky embedding vectors over the wire.
    chunks = [
        {"chunk_id": c.chunk_id, "doc_id": c.doc_id, "content": c.content, "metadata": c.metadata}
        for c in result.retrieved_chunks
    ]
    return APIResponse.ok(
        {
            "query": result.query,
            "answer": result.answer,
            "confidence": result.confidence,
            "retrieved_chunks": chunks,
        }
    )
