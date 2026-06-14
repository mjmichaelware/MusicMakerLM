from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator

from app.providers.base import LLMProvider, ProviderUnavailableError

if TYPE_CHECKING:
    from app.config import Settings


class OpenAIProvider(LLMProvider):
    """Stub — not implemented in the starting tree. See GitHub Issue #7."""

    def __init__(self, settings: "Settings") -> None:
        self._settings = settings

    async def complete(self, prompt: str) -> str:
        raise ProviderUnavailableError(
            "OpenAI provider not implemented in the starting tree. See GitHub Issue #7."
        )

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        raise ProviderUnavailableError(
            "OpenAI provider not implemented in the starting tree. See GitHub Issue #7."
        )
        yield  # make static analysis happy
