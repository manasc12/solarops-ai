"""RAG chain: retrieve -> rerank -> generate a grounded answer.

Produces the canonical ``RAGQueryResult``. The answer is grounded ONLY in
retrieved context. When no real LLM is configured, a deterministic extractive
summary of the top chunks is returned (still grounded), with source attribution.
"""

from __future__ import annotations

import re

from backend.app.core.logging import get_logger, log_event
from backend.app.core.security import sanitize_text
from backend.app.models.schemas import DocumentChunk, RAGQueryResult
from agents.shared.llm_client import get_llm_client
from rag.generation.prompts import RAG_PROMPT_TEMPLATE, RAG_SYSTEM
from rag.retrieval.reranker import rerank
from rag.retrieval.retriever import get_retriever

logger = get_logger("rag.chain")

_SENT = re.compile(r"(?<=[.!?])\s+")


class RAGChain:
    def __init__(self) -> None:
        self._retriever = get_retriever()
        self._llm = get_llm_client()

    def answer(self, query: str, top_k: int = 4) -> RAGQueryResult:
        query = sanitize_text(query, max_length=1000)
        scored = self._retriever.retrieve(query, top_k=top_k)
        scored = rerank(query, scored)
        chunks = [c for c, _ in scored]

        if not chunks:
            return RAGQueryResult(
                query=query,
                retrieved_chunks=[],
                answer="No maintenance knowledge is indexed to answer this question.",
                confidence=0.0,
            )

        context = self._format_context(chunks)
        prompt = RAG_PROMPT_TEMPLATE.format(context=context, query=query)
        fallback = self._extractive_answer(query, chunks)
        answer = self._llm.generate(prompt, system=RAG_SYSTEM, fallback=fallback)

        top_score = scored[0][1] if scored else 0.0
        confidence = round(min(1.0, max(0.0, top_score)), 3)
        log_event(logger, "rag_answered", query=query, n_chunks=len(chunks), confidence=confidence)
        return RAGQueryResult(
            query=query, retrieved_chunks=chunks, answer=answer, confidence=confidence
        )

    @staticmethod
    def _format_context(chunks: list[DocumentChunk]) -> str:
        parts = []
        for c in chunks:
            src = c.metadata.get("source", c.doc_id)
            parts.append(f"[{src}] {c.content}")
        return "\n\n".join(parts)

    @staticmethod
    def _extractive_answer(query: str, chunks: list[DocumentChunk]) -> str:
        q_terms = set(re.findall(r"[a-z0-9]+", query.lower()))
        best_sentences: list[str] = []
        sources: list[str] = []
        for chunk in chunks[:3]:
            src = chunk.metadata.get("source", chunk.doc_id)
            sentences = _SENT.split(chunk.content)
            ranked = sorted(
                sentences,
                key=lambda s: len(q_terms & set(re.findall(r"[a-z0-9]+", s.lower()))),
                reverse=True,
            )
            if ranked and ranked[0].strip():
                best_sentences.append(ranked[0].strip())
                if src not in sources:
                    sources.append(src)
        body = " ".join(best_sentences) if best_sentences else chunks[0].content[:300]
        citation = f" (sources: {', '.join(sources)})" if sources else ""
        return f"{body}{citation}"


_chain: RAGChain | None = None


def get_rag_chain() -> RAGChain:
    global _chain
    if _chain is None:
        _chain = RAGChain()
    return _chain
