"""Deterministic document loading and chunking.

Loads .md/.txt maintenance manuals and splits them into consistent, overlapping
chunks. Chunking is deterministic so the index is reproducible.
"""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from rag.toolbox.parse_pdf import parse_pdf
from rag.toolbox.parse_doc import parse_document
from rag.toolbox.chroma import SolarOpsChroma
from backend.app.core.logging import get_logger, log_event
from rag.toolbox.miscellaneous import document_id

logger = get_logger("rag.ingestion.load_docs")

_SUPPORTED = {".md", ".txt"}

def load_corpus(docs_dir: str, solarOpsChroma: SolarOpsChroma) -> list[str]:
    base = Path(docs_dir)
    if not base.exists():
        log_event(logger, "load_corpus_error", error=f"Directory {docs_dir} does not exist.")
        return []
    document_chunks: list[Document] = []
    try:
        for path in sorted(base.iterdir()):
            if path.suffix.lower() == ".pdf":
                document_chunks.extend(parse_pdf(path))
            elif path.suffix.lower() in _SUPPORTED:
                document_chunks.extend(parse_document(path))
        ids= [c.metadata.get("chunk_id",document_id(c.page_content)) for c in document_chunks]
        ids_list_added = solarOpsChroma.add_documents(document_chunks, ids=ids)
        log_event(logger, "load_corpus_success", n_chunks=len(document_chunks), n_added=len(ids_list_added))
        return ids_list_added
    except Exception as e:
        log_event(logger, "load_corpus_error", error=str(e))
        return []