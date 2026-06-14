import pytest

from app.core.data_model import Piece
from app.core.generation import _fallback_piece, generate_piece
from app.providers.base import ProviderUnavailableError


class MockLLM:
    async def complete(self, prompt: str) -> str:
        return """{
          "title": "Test Waltz",
          "composer": "Test",
          "tempo_bpm": 140,
          "parts": [{
            "name": "Piano",
            "instrument_midi": 0,
            "measures": [{
              "number": 1,
              "time_signature": "3/4",
              "tempo_bpm": null,
              "events": [
                {"kind": "note", "pitch": 60, "duration": 1.0, "velocity": 80, "offset": 0.0, "tied": false},
                {"kind": "note", "pitch": 64, "duration": 1.0, "velocity": 75, "offset": 1.0, "tied": false},
                {"kind": "note", "pitch": 67, "duration": 1.0, "velocity": 75, "offset": 2.0, "tied": false}
              ]
            }]
          }]
        }"""

    async def stream(self, prompt: str):
        yield ""


class FailLLM:
    async def complete(self, prompt: str) -> str:
        raise ProviderUnavailableError("no llm")

    async def stream(self, prompt: str):
        yield ""


class BadJsonLLM:
    async def complete(self, prompt: str) -> str:
        return "not json at all"

    async def stream(self, prompt: str):
        yield ""


@pytest.mark.asyncio
async def test_generate_valid_json():
    piece = await generate_piece("happy waltz", MockLLM())
    assert isinstance(piece, Piece)
    assert piece.title == "Test Waltz"
    assert piece.tempo_bpm == 140


@pytest.mark.asyncio
async def test_generate_falls_back_on_unavailable():
    piece = await generate_piece("happy waltz", FailLLM())
    assert isinstance(piece, Piece)
    assert "stub" in piece.composer.lower()


@pytest.mark.asyncio
async def test_generate_falls_back_on_bad_json():
    piece = await generate_piece("happy waltz", BadJsonLLM())
    assert isinstance(piece, Piece)
    assert "stub" in piece.composer.lower()


def test_fallback_piece_is_valid():
    p = _fallback_piece("test prompt")
    assert len(p.parts) == 1
    assert len(p.parts[0].measures) == 4


def test_to_midi_returns_valid_bytes():
    p = _fallback_piece("test")
    midi = p.to_midi()
    assert isinstance(midi, bytes)
    assert midi[:4] == b"MThd"


def test_to_midi_chord():
    from app.core.data_model import Chord, Measure, Note, Part, Piece
    chord = Chord(
        kind="chord",
        notes=[
            Note(kind="note", pitch=60, duration=1.0, velocity=80, offset=0.0),
            Note(kind="note", pitch=64, duration=1.0, velocity=80, offset=0.0),
            Note(kind="note", pitch=67, duration=1.0, velocity=80, offset=0.0),
        ],
        duration=1.0,
        offset=0.0,
    )
    piece = Piece(
        title="Chord test",
        parts=[Part(measures=[Measure(number=1, events=[chord])])],
    )
    midi = piece.to_midi()
    assert midi[:4] == b"MThd"
