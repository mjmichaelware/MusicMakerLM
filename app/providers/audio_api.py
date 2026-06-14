from __future__ import annotations

from typing import TYPE_CHECKING

from app.providers.base import AudioProvider, ProviderUnavailableError

if TYPE_CHECKING:
    from app.config import Settings


class APIAudioProvider(AudioProvider):
    """Stub — not implemented in the starting tree. See GitHub Issue #8."""

    def __init__(self, settings: "Settings") -> None:
        self._settings = settings

    async def synthesize(self, midi_bytes: bytes, sf2_path: str = "") -> bytes:
        raise ProviderUnavailableError(
            "Paid audio API provider not implemented in the starting tree. See GitHub Issue #8."
        )
