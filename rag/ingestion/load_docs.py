"""Deterministic document loading and chunking.

Loads .md/.txt maintenance manuals and splits them into consistent, overlapping
chunks. Chunking is deterministic so the index is reproducible.
"""

from __future__ import annotations

from pathlib import Path

from backend.app.models.schemas import DocumentChunk
from backend.app.utils.helpers import new_id

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
_SUPPORTED = {".md", ".txt"}


def _chunk_text(text: str, size: int, overlap: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    step = max(1, size - overlap)
    for start in range(0, len(words), step):
        window = words[start : start + size]
        if window:
            chunks.append(" ".join(window))
        if start + size >= len(words):
            break
    return chunks


def load_document(path: Path) -> list[DocumentChunk]:
    text = path.read_text(encoding="utf-8")
    doc_id = path.stem
    chunks: list[DocumentChunk] = []
    for i, content in enumerate(_chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)):
        chunks.append(
            DocumentChunk(
                doc_id=doc_id,
                chunk_id=f"{doc_id}::{i}",
                content=content,
                embedding=None,
                metadata={"source": path.name, "doc_id": doc_id, "chunk_index": i},
            )
        )
    return chunks


def load_corpus(docs_dir: str) -> list[DocumentChunk]:
    base = Path(docs_dir)
    if not base.exists():
        return []
    chunks: list[DocumentChunk] = []
    for path in sorted(base.iterdir()):
        if path.suffix.lower() == ".pdf":
            from rag.ingestion.parse_pdf import parse_pdf

            chunks.extend(parse_pdf(path))
        elif path.suffix.lower() in _SUPPORTED:
            chunks.extend(load_document(path))
    return chunks


# keep import available for callers needing a unique id helper
_ = new_id
