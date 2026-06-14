from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, AsyncIterator

if TYPE_CHECKING:
    from app.config import Settings


class ProviderUnavailableError(Exception):
    """Raised when a provider backend is not reachable or not installed."""


class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, prompt: str) -> str: ...

    @abstractmethod
    async def stream(self, prompt: str) -> AsyncIterator[str]: ...


class AudioProvider(ABC):
    @abstractmethod
    async def synthesize(self, midi_bytes: bytes, sf2_path: str) -> bytes:
        """Return WAV bytes synthesized from MIDI bytes and a soundfont path."""
        ...


def get_llm_provider(settings: "Settings") -> LLMProvider:
    if settings.llm_provider == "local":
        from app.providers.llm_local import OllamaProvider
        return OllamaProvider(settings)
    if settings.llm_provider == "openai":
        from app.providers.llm_api import OpenAIProvider
        return OpenAIProvider(settings)
    raise ValueError(f"Unknown LLM provider: {settings.llm_provider!r}")


def get_audio_provider(settings: "Settings") -> AudioProvider:
    if settings.audio_provider == "local":
        from app.providers.audio_local import FluidSynthProvider
        return FluidSynthProvider(settings)
    if settings.audio_provider == "api":
        from app.providers.audio_api import APIAudioProvider
        return APIAudioProvider(settings)
    raise ValueError(f"Unknown audio provider: {settings.audio_provider!r}")
