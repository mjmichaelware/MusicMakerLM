import json
from typing import AsyncIterator

import httpx

from app.providers.base import LLMProvider, ProviderUnavailableError


class OllamaProvider(LLMProvider):
    def __init__(self, settings) -> None:
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
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise ProviderUnavailableError(f"Ollama unreachable: {e}") from e
        except httpx.HTTPStatusError as e:
            raise ProviderUnavailableError(f"Ollama HTTP error: {e}") from e
        except (KeyError, json.JSONDecodeError) as e:
            raise ProviderUnavailableError(f"Ollama unexpected response: {e}") from e

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        try:
            async with self._client.stream(
                "POST",
                "/api/generate",
                json={"model": self._model, "prompt": prompt, "stream": True},
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    yield obj.get("response", "")
                    if obj.get("done"):
                        break
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise ProviderUnavailableError(f"Ollama unreachable: {e}") from e
        except httpx.HTTPStatusError as e:
            raise ProviderUnavailableError(f"Ollama HTTP error: {e}") from e
