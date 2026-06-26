"""RAG knowledge endpoints. Routes only — logic lives in the RAG chain."""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.models.requests import RAGQueryRequest
from backend.app.models.responses import APIResponse
from backend.app.models.schemas import RAGQueryResult
from rag.generation.rag_chain import get_rag_chain

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/query", response_model=APIResponse)
def query_knowledge(req: RAGQueryRequest) -> APIResponse:
    result: RAGQueryResult = get_rag_chain().answer(req.query, top_k=req.top_k)
    # Avoid returning bulky embedding vectors over the wire.
    chunks = [
        {"chunk_id": c.metadata.get("chunk_id", "unknown"), "doc_id": c.metadata.get("doc_id", "unknown"), "content": c.page_content, "metadata": c.metadata}
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
