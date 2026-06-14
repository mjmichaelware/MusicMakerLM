from __future__ import annotations

from typing import Optional

from app.core.data_model import Piece
from app.providers.base import AudioProvider, ProviderUnavailableError


async def render_to_midi(piece: Piece) -> bytes:
    return piece.to_midi()


async def render_to_wav(
    piece: Piece, provider: AudioProvider, sf2_path: str = ""
) -> Optional[bytes]:
    """
    Returns WAV bytes, or None if the audio provider is unavailable.
    Callers must handle None gracefully.
    """
    try:
        midi_bytes = piece.to_midi()
        return await provider.synthesize(midi_bytes, sf2_path)
    except ProviderUnavailableError:
        return None
