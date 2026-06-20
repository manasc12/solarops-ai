"""Lightweight security helpers: input sanitization and LLM output cleaning.

No authentication is implemented (out of scope), but external inputs and LLM
outputs are sanitized before downstream use per the security constraints.
"""

from __future__ import annotations

import re

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_FARM_ID = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")


def sanitize_text(text: str, max_length: int = 8000) -> str:
    """Strip control characters and clamp length of free-form text."""
    if not isinstance(text, str):
        text = str(text)
    cleaned = _CONTROL_CHARS.sub("", text).strip()
    return cleaned[:max_length]


def sanitize_llm_output(text: str, max_length: int = 8000) -> str:
    """Sanitize model output before it is stored or surfaced downstream."""
    cleaned = sanitize_text(text, max_length=max_length)
    # Remove obvious prompt-injection echoes of system markers.
    cleaned = cleaned.replace("```", "").strip()
    return cleaned


def is_valid_farm_id(farm_id: str) -> bool:
    return bool(_FARM_ID.match(farm_id or ""))


def require_valid_farm_id(farm_id: str) -> str:
    if not is_valid_farm_id(farm_id):
        raise ValueError(f"Invalid farm_id: {farm_id!r}")
    return farm_id
