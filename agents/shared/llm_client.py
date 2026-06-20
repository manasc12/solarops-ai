"""LLM client with a deterministic offline fallback.

Real OpenAI calls are used only when an API key is configured AND mock mode is
off. Otherwise a deterministic, grounded template generator is used so the
system runs fully offline and tests are reproducible. LLM use is restricted to
reasoning/explanation tasks (RCA, reporting, RAG answering).

All outputs are sanitized before being returned.
"""

from __future__ import annotations

from backend.app.core.config import settings
from backend.app.core.logging import get_logger, log_event
from backend.app.core.security import sanitize_llm_output

logger = get_logger("agents.llm")


class LLMClient:
    def __init__(self) -> None:
        self._enabled = settings.llm_enabled

    @property
    def mode(self) -> str:
        return "openai" if self._enabled else "deterministic"

    def generate(self, prompt: str, system: str = "", fallback: str | None = None) -> str:
        """Return a completion for ``prompt``.

        ``fallback`` is the deterministic text used when no real LLM is wired;
        it MUST already be grounded in structured context by the caller.
        """
        if self._enabled:
            try:
                return sanitize_llm_output(self._openai(prompt, system))
            except Exception as exc:  # never fail silently; degrade gracefully
                log_event(logger, "llm_call_failed", error=str(exc))
        text = fallback if fallback is not None else prompt
        return sanitize_llm_output(text)

    def _openai(self, prompt: str, system: str) -> str:  # pragma: no cover - needs key
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        resp = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system or "You are a solar operations analyst."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        log_event(logger, "llm_call_ok", model=settings.openai_model)
        return resp.choices[0].message.content or ""


_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
