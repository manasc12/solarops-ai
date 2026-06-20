"""Embedding generation.

Default: a deterministic, dependency-free hashing embedding (hashed bag-of-words,
L2-normalized) so the RAG system runs fully offline and reproducibly. If
``sentence-transformers`` is installed it is used automatically for higher quality.
"""

from __future__ import annotations

import hashlib
import math
import re

_DIM = 256
_TOKEN = re.compile(r"[a-z0-9]+")
_model = None
_use_st = False


def _try_load_st() -> bool:
    global _model, _use_st
    if _model is not None:
        return _use_st
    try:  # pragma: no cover - optional dependency
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")
        _use_st = True
    except Exception:
        _model = False
        _use_st = False
    return _use_st


def _tokens(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


def _hash_embed(text: str) -> list[float]:
    vec = [0.0] * _DIM
    for tok in _tokens(text):
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        idx = h % _DIM
        sign = 1.0 if (h >> 8) & 1 else -1.0
        vec[idx] += sign
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def embed(text: str) -> list[float]:
    if _try_load_st():  # pragma: no cover - optional path
        return _model.encode(text, normalize_embeddings=True).tolist()
    return _hash_embed(text)


def embed_batch(texts: list[str]) -> list[list[float]]:
    return [embed(t) for t in texts]


def dimension() -> int:
    return _DIM
