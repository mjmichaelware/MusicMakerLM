from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, AsyncIterator

import httpx

from app.providers.base import LLMProvider, ProviderUnavailableError

if TYPE_CHECKING:
    from app.config import Settings

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    def __init__(self, settings: "Settings") -> None:
        self._model = settings.ollama_model
        self._client = httpx.AsyncClient(
            base_url=settings.ollama_host,
            timeout=httpx.Timeout(120.0),
        )

    async def complete(self, prompt: str) -> str:
        try:
            r = await self._client.post(
                "/api/generate",
                json={"model": self._model, "prompt": prompt, "stream": False},
            )
            r.raise_for_status()
            return r.json()["response"]
        except (httpx.ConnectError, httpx.HTTPStatusError, httpx.ReadTimeout) as e:
            raise ProviderUnavailableError(f"Ollama unavailable: {e}") from e

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        try:
            async with self._client.stream(
                "POST",
                "/api/generate",
                json={"model": self._model, "prompt": prompt, "stream": True},
            ) as resp:
                async for line in resp.aiter_lines():
                    if line:
                        obj = json.loads(line)
                        yield obj.get("response", "")
                        if obj.get("done"):
                            break
        except (httpx.ConnectError, httpx.HTTPStatusError) as e:
            raise ProviderUnavailableError(f"Ollama unavailable: {e}") from e
