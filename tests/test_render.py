from unittest.mock import AsyncMock, patch

import pytest

from app.core.generation import _fallback_piece
from app.core.render_audio import render_to_midi, render_to_wav
from app.core.render_notation import render_to_musicxml, render_to_svg
from app.providers.base import ProviderUnavailableError


@pytest.mark.asyncio
async def test_render_to_midi_magic_bytes():
    p = _fallback_piece("test")
    midi = await render_to_midi(p)
    assert isinstance(midi, bytes)
    assert midi[:4] == b"MThd"


def test_render_to_musicxml_contains_score_partwise():
    p = _fallback_piece("test")
    xml = render_to_musicxml(p)
    assert isinstance(xml, str)
    assert "score-partwise" in xml


def test_render_to_svg_fallback_is_nonempty():
    """When Verovio is not installed, render_to_svg returns a non-empty fallback string."""
    p = _fallback_piece("test")
    result = render_to_svg(p)
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_render_to_wav_returns_none_when_unavailable():
    """render_to_wav returns None when the provider raises ProviderUnavailableError."""
    from app.providers.base import AudioProvider

    class UnavailableAudio(AudioProvider):
        async def synthesize(self, midi_bytes: bytes, sf2_path: str) -> bytes:
            raise ProviderUnavailableError("no fluidsynth in test")

    p = _fallback_piece("test")
    result = await render_to_wav(p, UnavailableAudio())
    assert result is None


@pytest.mark.asyncio
async def test_render_to_wav_returns_bytes_when_available():
    """render_to_wav returns bytes when the provider succeeds."""
    from app.providers.base import AudioProvider

    fake_wav = b"RIFF" + b"\x00" * 36  # minimal fake WAV header

    class FakeAudio(AudioProvider):
        async def synthesize(self, midi_bytes: bytes, sf2_path: str) -> bytes:
            return fake_wav

    p = _fallback_piece("test")
    result = await render_to_wav(p, FakeAudio())
    assert result == fake_wav
