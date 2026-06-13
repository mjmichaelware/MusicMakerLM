from abc import ABC, abstractmethod
from typing import AsyncIterator


class ProviderUnavailableError(Exception):
    """Raised at call time when a backend is unreachable or not installed."""


class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, prompt: str) -> str: ...

    @abstractmethod
    async def stream(self, prompt: str) -> AsyncIterator[str]: ...


class AudioProvider(ABC):
    @abstractmethod
    async def synthesize(self, midi_bytes: bytes, sf2_path: str) -> bytes:
        """Return WAV bytes synthesized from MIDI bytes via the given soundfont."""
        ...


class _UnknownLLMProvider(LLMProvider):
    def __init__(self, name: str) -> None:
        self._name = name

    async def complete(self, prompt: str) -> str:
        raise ProviderUnavailableError(f"Unknown LLM provider: {self._name!r}")

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        raise ProviderUnavailableError(f"Unknown LLM provider: {self._name!r}")
        yield  # make it an async generator


class _UnknownAudioProvider(AudioProvider):
    def __init__(self, name: str) -> None:
        self._name = name

    async def synthesize(self, midi_bytes: bytes, sf2_path: str) -> bytes:
        raise ProviderUnavailableError(f"Unknown audio provider: {self._name!r}")


def get_llm_provider(settings) -> LLMProvider:
    """Factory — reads settings.llm_provider, returns the concrete provider.
    Never raises; ProviderUnavailableError surfaces on first complete()/stream() call.
    """
    if settings.llm_provider == "local":
        from app.providers.llm_local import OllamaProvider
        return OllamaProvider(settings)
    if settings.llm_provider == "openai":
        from app.providers.llm_api import OpenAIProvider
        return OpenAIProvider(settings)
    return _UnknownLLMProvider(settings.llm_provider)


def get_audio_provider(settings) -> AudioProvider:
    """Factory — reads settings.audio_provider, returns the concrete provider.
    Never raises; ProviderUnavailableError surfaces on first synthesize() call.
    """
    if settings.audio_provider == "local":
        from app.providers.audio_local import FluidSynthProvider
        return FluidSynthProvider(settings)
    if settings.audio_provider == "api":
        from app.providers.audio_api import APIAudioProvider
        return APIAudioProvider(settings)
    return _UnknownAudioProvider(settings.audio_provider)
