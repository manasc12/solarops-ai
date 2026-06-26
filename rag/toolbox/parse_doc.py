from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from backend.app.core.config import settings
from backend.app.core.logging import get_logger, log_event
from rag.toolbox.miscellaneous import document_id, chunk_text

logger = get_logger("rag.toolbox.parse_doc")

def parse_document(path: Path) -> list[Document]:
    text = path.read_text(encoding="utf-8")
    doc_id = path.stem
    document_chunks: list[Document] = []
    try:
        for _, content in enumerate(chunk_text(text, settings.chunk_size, settings.chunk_overlap)):
            document_chunks.append(
                Document(
                    page_content=content,
                    metadata={"source": path.name, "doc_id": doc_id, "chunk_id": document_id(content)},
                )
            )
        log_event(logger, "parse_document_success", file=str(path), n_chunks=len(document_chunks))
        return document_chunks
    except Exception as e:
        log_event(logger, "parse_document_error", file=str(path), error=str(e))
        return []