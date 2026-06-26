"""Lightweight lexical reranker.

Re-orders semantically retrieved chunks by query-term overlap to sharpen the
final ranking. Combines the semantic score with a lexical bonus.
"""

from __future__ import annotations

import re
import numpy as np
from collections import Counter
from langchain_core.documents import Document

_TOKEN = re.compile(r"[a-z0-9]+")


def _terms(text: str) -> set[str]:
    return set(_TOKEN.findall(text.lower()))

def weighted_overlap(query_terms, doc_terms):
    doc_counts = Counter(doc_terms)
    return sum(doc_counts[t] for t in query_terms)

def softmax_normalize(scores): # use only if applicable
    exp = np.exp(scores - np.max(scores))
    return exp / exp.sum()

def minmax_normalize(scores):
    scores = np.array(scores)
    if len(scores) == 0:
        return scores

    min_s, max_s = scores.min(), scores.max()
    if min_s == max_s:
        return np.ones_like(scores)

    return (scores - min_s) / (max_s - min_s)

def rerank(
    query: str, scored: list[tuple[Document, float]]
) -> list[tuple[Document, float]]:
    q_terms = _terms(query)
    if not q_terms:
        return scored
    document_chunks, chroma_cosine_distance_scores = zip(*scored) if scored else ([], [])
    chroma_cosine_similarity_scores = [1 - s for s in chroma_cosine_distance_scores] # by subtracting from 1 u turn the distance into cosine similarity scores
    
    # Simple Lexical overlap method is used here for calculating Lexical similarity but we can replace this with BM25 or any other appropriate lexical similarity calculator in future
    # overlap_similarity_scores_not_normalized = [len(q_terms & _terms(d_chunk.page_content)) / len(q_terms) for d_chunk in document_chunks] # Version 1
    overlap_similarity_scores_not_normalized = [weighted_overlap(q_terms, _terms(d_chunk.page_content)) for d_chunk in document_chunks] # Version 2
    # overlap_similarity_scores = minmax_normalize(overlap_similarity_scores_not_normalized) # Version 1
    overlap_similarity_scores = softmax_normalize(overlap_similarity_scores_not_normalized) # Version 2

    reranked: list[tuple[Document, float]] = []
    for d_chunk, chroma_cosine, overlap in zip(document_chunks, chroma_cosine_similarity_scores, overlap_similarity_scores):
        # A weighted linear score fusion reranker (normalized dense + sparse hybrid reranker) is used here 
        # It combines the semantic score with a lexical bonus to produce a final score for each document chunk. 
        # The weights can be adjusted based on the importance of semantic vs lexical similarity in the specific use case.
        # However we are open to replace this with any other hybrid reranker like RRF, CrossEncoder, LambdaMART, RankNet etc. in future.
        combined = 0.7 * chroma_cosine + 0.3 * overlap 
        reranked.append((d_chunk, round(combined, 4)))
    reranked.sort(key=lambda s: s[1], reverse=True)
    return reranked
