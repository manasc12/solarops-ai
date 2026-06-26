"""Retriever: semantic search over the maintenance knowledge base.

Ensures the index exists (building it from the manuals on first use), then
returns the most relevant chunks for a query, with optional metadata filtering.
"""

from __future__ import annotations

from backend.app.core.config import settings
from backend.app.core.logging import get_logger, log_event
from rag.ingestion.load_docs import load_corpus
from langchain_core.documents import Document
from rag.toolbox.chroma import SolarOpsChroma

logger = get_logger("rag.retrieval.retriever")


class Retriever:
    def __init__(self) -> None:
        self._store: SolarOpsChroma = SolarOpsChroma()

    def ensure_index(self) -> int:
        if self._store.size > 0:
            return self._store.size
        try:
            ids_list_added = load_corpus(settings.rag_docs_dir, self._store)
            if self._store.size == len(ids_list_added):
                log_event(logger, "ChromaDB_index_creation_success", n_chunks=self._store.size)
            return self._store.size
        except Exception as e:
            log_event(logger, "ChromaDB_index_creation_error", error=str(e))
            return self._store.size

    def retrieve(
        self, query: str, top_k: int | None = None, metadata_filter: dict | None = None
    ) -> list[tuple[Document, float]]:
        self.ensure_index()
        top_k = top_k or settings.rag_top_k
        try:
            # 1. This returns a list of tuples (Document, score)
            # 2. The score returned is the cosine distance (0 = identical, 1 = orthogonal, 2 = opposite)
            return self._store.similarity_search_with_score(query, k=top_k, filter=metadata_filter) 
        except Exception as e:
            log_event(logger, "ChromaDB_retrieve_error", error=str(e))
            return []


_retriever: Retriever | None = None


def get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever
