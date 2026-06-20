"""Retriever: semantic search over the maintenance knowledge base.

Ensures the index exists (building it from the manuals on first use), then
returns the most relevant chunks for a query, with optional metadata filtering.
"""

from __future__ import annotations

from backend.app.core.config import settings
from backend.app.core.logging import get_logger, log_event
from backend.app.models.schemas import DocumentChunk
from rag.indexing.vector_store import get_vector_store
from rag.ingestion.load_docs import load_corpus

logger = get_logger("rag.retriever")


class Retriever:
    def __init__(self) -> None:
        self._store = get_vector_store()

    def ensure_index(self) -> int:
        if self._store.size > 0:
            return self._store.size
        if self._store.load():
            log_event(logger, "rag_index_loaded", n_chunks=self._store.size)
            return self._store.size
        chunks = load_corpus(settings.rag_docs_dir)
        self._store.build(chunks)
        self._store.save()
        log_event(logger, "rag_index_created", n_chunks=self._store.size)
        return self._store.size

    def retrieve(
        self, query: str, top_k: int | None = None, metadata_filter: dict | None = None
    ) -> list[tuple[DocumentChunk, float]]:
        self.ensure_index()
        top_k = top_k or settings.rag_top_k
        return self._store.search(query, top_k=top_k, metadata_filter=metadata_filter)


_retriever: Retriever | None = None


def get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever
