import pytest
from unittest.mock import AsyncMock

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


def test_render_to_musicxml_contains_marker():
    p = _fallback_piece("test")
    xml = render_to_musicxml(p)
    assert isinstance(xml, str)
    assert "score-partwise" in xml


def test_render_to_svg_returns_non_empty_string():
    # Verovio likely not installed in CI — fallback string is fine
    p = _fallback_piece("test")
    result = render_to_svg(p)
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_render_to_wav_returns_none_when_unavailable():
    """render_to_wav must return None, not raise, when the provider is unavailable."""
    p = _fallback_piece("test")

    class FailAudio:
        async def synthesize(self, midi_bytes, sf2_path):
            raise ProviderUnavailableError("no fluidsynth")

    result = await render_to_wav(p, FailAudio())
    assert result is None


@pytest.mark.asyncio
async def test_render_to_wav_returns_bytes_when_provider_works():
    p = _fallback_piece("test")
    fake_wav = b"RIFF\x00\x00\x00\x00WAVE"

    class FakeAudio:
        async def synthesize(self, midi_bytes, sf2_path):
            return fake_wav

    result = await render_to_wav(p, FakeAudio())
    assert result == fake_wav
