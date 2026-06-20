"""Lightweight lexical reranker.

Re-orders semantically retrieved chunks by query-term overlap to sharpen the
final ranking. Combines the semantic score with a lexical bonus.
"""

from __future__ import annotations

import re

from backend.app.models.schemas import DocumentChunk

_TOKEN = re.compile(r"[a-z0-9]+")


def _terms(text: str) -> set[str]:
    return set(_TOKEN.findall(text.lower()))


def rerank(
    query: str, scored: list[tuple[DocumentChunk, float]]
) -> list[tuple[DocumentChunk, float]]:
    q_terms = _terms(query)
    if not q_terms:
        return scored

    reranked: list[tuple[DocumentChunk, float]] = []
    for chunk, sem in scored:
        overlap = len(q_terms & _terms(chunk.content)) / len(q_terms)
        combined = 0.7 * sem + 0.3 * overlap
        reranked.append((chunk, round(combined, 4)))
    reranked.sort(key=lambda s: s[1], reverse=True)
    return reranked
