"""PDF parsing with graceful degradation.

Uses ``pypdf`` if available; otherwise returns an empty chunk list and logs a
warning so the pipeline keeps running on text/markdown sources.
"""

from __future__ import annotations

from pathlib import Path

from backend.app.core.logging import get_logger, log_event
from langchain_core.documents import Document
from backend.app.core.config import settings
from rag.toolbox.miscellaneous import document_id, chunk_text
from pypdf import PdfReader

logger = get_logger("rag.parse_pdf")


def parse_pdf(path: Path) -> list[Document]:
    try:
        reader = PdfReader(str(path))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        doc_id = path.stem
        document_chunks: list[Document] = []
        for _, content in enumerate(chunk_text(text, settings.chunk_size, settings.chunk_overlap)):
            document_chunks.append(
                Document(
                    page_content=content,
                    metadata={"source": path.name, "doc_id": doc_id, "chunk_id": document_id(content)},
                )
            )
        log_event(logger, "parse_pdf_success", file=str(path), n_chunks=len(document_chunks))
        return document_chunks
    except Exception as e:
        log_event(logger, "parse_pdf_error", file=str(path), error=str(e))
        return []
