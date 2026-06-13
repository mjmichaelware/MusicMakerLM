from typing import AsyncIterator

from app.providers.base import LLMProvider, ProviderUnavailableError


class OpenAIProvider(LLMProvider):
    """Stub — constructor succeeds; methods raise until Issue #7 is implemented."""

    def __init__(self, settings) -> None:
        self._settings = settings

    async def complete(self, prompt: str) -> str:
        raise ProviderUnavailableError(
            "OpenAI provider not implemented in the starting tree. See GitHub Issue #7."
        )

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        raise ProviderUnavailableError(
            "OpenAI provider not implemented in the starting tree. See GitHub Issue #7."
        )
        yield  # make it an async generator
