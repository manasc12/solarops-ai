"""PDF parsing with graceful degradation.

Uses ``pypdf`` if available; otherwise returns an empty chunk list and logs a
warning so the pipeline keeps running on text/markdown sources.
"""

from __future__ import annotations

from pathlib import Path

from backend.app.core.logging import get_logger, log_event
from backend.app.models.schemas import DocumentChunk

logger = get_logger("rag.parse_pdf")


def parse_pdf(path: Path) -> list[DocumentChunk]:
    try:
        from pypdf import PdfReader
    except Exception:
        log_event(logger, "pypdf_unavailable", file=str(path))
        return []

    from rag.ingestion.load_docs import CHUNK_OVERLAP, CHUNK_SIZE, _chunk_text

    reader = PdfReader(str(path))
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    doc_id = path.stem
    chunks: list[DocumentChunk] = []
    for i, content in enumerate(_chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)):
        chunks.append(
            DocumentChunk(
                doc_id=doc_id,
                chunk_id=f"{doc_id}::{i}",
                content=content,
                metadata={"source": path.name, "doc_id": doc_id, "chunk_index": i},
            )
        )
    return chunks
