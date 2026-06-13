from __future__ import annotations

import logging
from typing import Optional

from app.core.data_model import Piece
from app.providers.base import AudioProvider, ProviderUnavailableError

logger = logging.getLogger(__name__)


async def render_to_midi(piece: Piece) -> bytes:
    return piece.to_midi()


async def render_to_wav(
    piece: Piece, provider: AudioProvider, sf2_path: str = ""
) -> Optional[bytes]:
    """Synthesize WAV. Returns None if FluidSynth (or the provider) is unavailable."""
    try:
        midi_bytes = piece.to_midi()
        return await provider.synthesize(midi_bytes, sf2_path)
    except ProviderUnavailableError as e:
        logger.info("Audio provider unavailable (%s) — wav_b64 will be null", e)
        return None
    except Exception as e:
        logger.warning("Unexpected render_to_wav error (%s) — returning None", e)
        return None
