"""In-memory vector store with disk persistence.

A simple cosine-similarity store over ``DocumentChunk`` embeddings. Avoids heavy
vector-DB dependencies while preserving the retrieval interface (semantic search
+ metadata filtering). FAISS could be swapped in behind this same API later.
"""

from __future__ import annotations

import pickle
from pathlib import Path

from backend.app.core.config import settings
from backend.app.core.logging import get_logger, log_event
from backend.app.models.schemas import DocumentChunk
from rag.indexing.embeddings import embed, embed_batch

logger = get_logger("rag.vector_store")
_INDEX_FILE = "vector_index.pkl"


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))  # inputs are L2-normalized


class VectorStore:
    def __init__(self) -> None:
        self._chunks: list[DocumentChunk] = []

    # ── build / persist ─────────────────────────────────────────────────────
    def build(self, chunks: list[DocumentChunk]) -> None:
        embeddings = embed_batch([c.content for c in chunks])
        for chunk, vec in zip(chunks, embeddings):
            chunk.embedding = vec
        self._chunks = chunks
        log_event(logger, "vector_store_built", n_chunks=len(chunks))

    def save(self, index_dir: str | None = None) -> Path:
        index_dir = index_dir or settings.rag_index_dir
        path = Path(index_dir)
        path.mkdir(parents=True, exist_ok=True)
        target = path / _INDEX_FILE
        with target.open("wb") as fh:
            pickle.dump([c.model_dump() for c in self._chunks], fh)
        return target

    def load(self, index_dir: str | None = None) -> bool:
        index_dir = index_dir or settings.rag_index_dir
        target = Path(index_dir) / _INDEX_FILE
        if not target.exists():
            return False
        with target.open("rb") as fh:
            raw = pickle.load(fh)
        self._chunks = [DocumentChunk(**c) for c in raw]
        return True

    # ── query ───────────────────────────────────────────────────────────────
    def search(
        self, query: str, top_k: int = 4, metadata_filter: dict | None = None
    ) -> list[tuple[DocumentChunk, float]]:
        q = embed(query)
        candidates = self._chunks
        if metadata_filter:
            candidates = [
                c
                for c in candidates
                if all(c.metadata.get(k) == v for k, v in metadata_filter.items())
            ]
        scored = [
            (c, _cosine(q, c.embedding)) for c in candidates if c.embedding is not None
        ]
        scored.sort(key=lambda s: s[1], reverse=True)
        return scored[:top_k]

    @property
    def size(self) -> int:
        return len(self._chunks)


_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
