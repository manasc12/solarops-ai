"""RAG chain: retrieve -> rerank -> generate a grounded answer.

Produces the canonical ``RAGQueryResult``. The answer is grounded ONLY in
retrieved context. When no real LLM is configured, a deterministic extractive
summary of the top chunks is returned (still grounded), with source attribution.
"""

from __future__ import annotations

import re

from backend.app.core.logging import get_logger, log_event
from backend.app.core.security import sanitize_text
from backend.app.models.schemas import RAGQueryResult
from langchain_core.documents import Document
from agents.shared.llm_client import get_llm_client
from rag.generation.prompts import RAG_PROMPT_TEMPLATE, RAG_SYSTEM
from rag.retrieval.reranker import rerank
from rag.retrieval.retriever import get_retriever
from backend.app.core.config import settings

logger = get_logger("rag.generation.rag_chain")

_SENT = re.compile(r"(?<=[.!?])\s+")


class RAGChain:
    def __init__(self) -> None:
        self._retriever = get_retriever()
        self._llm = get_llm_client()

    def answer(self, query: str, top_k: int = settings.rag_top_k) -> RAGQueryResult:
        query = sanitize_text(query, max_length=1000)
        distance_scored = self._retriever.retrieve(query, top_k=top_k)
        similarity_scored = rerank(query, distance_scored)
        document_chunks = [c for c, _ in similarity_scored]

        if not document_chunks:
            return RAGQueryResult(
                query=query,
                retrieved_chunks=[],
                answer="No maintenance knowledge is indexed to answer this question.",
                confidence=0.0,
            )

        context = self._format_context(document_chunks)
        prompt = RAG_PROMPT_TEMPLATE.format(context=context, query=query)
        fallback = self._extractive_answer(query, document_chunks)
        answer = self._llm.generate(prompt, system=RAG_SYSTEM, fallback=fallback)

        top_score = similarity_scored[0][1] if similarity_scored else 0.0
        confidence = round(min(1.0, max(0.0, top_score)), 3)
        log_event(logger, "rag_answer_success", query=query, n_chunks=len(document_chunks), confidence=confidence)
        return RAGQueryResult(
            query=query, retrieved_chunks=document_chunks, answer=answer, confidence=confidence
        )

    @staticmethod
    def _format_context(chunks: list[Document]) -> str:
        parts = []
        for i, c in enumerate(chunks):
            src = c.metadata.get("source", "unknown")
            parts.append(f"{i+1}.[{src}] \n {c.page_content}")
        return "\n\n---\n\n".join(parts)

    @staticmethod
    def _extractive_answer(query: str, chunks: list[Document]) -> str:
        q_terms = set(re.findall(r"[a-z0-9]+", query.lower()))
        best_sentences: list[str] = []
        sources: list[str] = []
        for chunk in chunks[:3]:
            src = chunk.metadata.get("source", "unknown")
            sentences = _SENT.split(chunk.page_content)
            ranked = sorted(
                sentences,
                key=lambda s: len(q_terms & set(re.findall(r"[a-z0-9]+", s.lower()))),
                reverse=True,
            )
            if ranked and ranked[0].strip():
                best_sentences.append(ranked[0].strip())
                if src not in sources:
                    sources.append(src)
        body = " ".join(best_sentences) if best_sentences else chunks[0].page_content[:300]
        citation = f" (sources: {', '.join(sources)})" if sources else ""
        return f"{body}{citation}"


_chain: RAGChain | None = None


def get_rag_chain() -> RAGChain:
    global _chain
    if _chain is None:
        _chain = RAGChain()
    return _chain

if __name__ == "__main__": #TODO: remove this test code and add proper unit tests for RAG chain
    # Quick test
    chain = get_rag_chain()
    result = chain.answer("How do I handle a degraded inverter?")
    from pprint import pprint
    pprint(result.model_dump())