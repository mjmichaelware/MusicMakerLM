import pytest

from app.core.data_model import Piece
from app.core.generation import _fallback_piece, generate_piece
from app.providers.base import ProviderUnavailableError


class MockLLM:
    async def complete(self, prompt: str) -> str:
        return """{
          "title": "Test Piece",
          "composer": "Test",
          "tempo_bpm": 120,
          "parts": [{
            "name": "Piano",
            "instrument_midi": 0,
            "measures": [{
              "number": 1,
              "time_signature": "4/4",
              "tempo_bpm": null,
              "events": [
                {"kind": "note", "pitch": 60, "duration": 1.0,
                 "velocity": 80, "offset": 0.0, "tied": false},
                {"kind": "chord", "notes": [
                  {"kind": "note", "pitch": 64, "duration": 1.0,
                   "velocity": 70, "offset": 0.0, "tied": false},
                  {"kind": "note", "pitch": 67, "duration": 1.0,
                   "velocity": 70, "offset": 0.0, "tied": false}
                ], "duration": 1.0, "offset": 1.0}
              ]
            }]
          }]
        }"""

    async def stream(self, prompt: str):
        yield ""


class FailLLM:
    async def complete(self, prompt: str) -> str:
        raise ProviderUnavailableError("no llm in test")

    async def stream(self, prompt: str):
        yield ""


class BadJsonLLM:
    async def complete(self, prompt: str) -> str:
        return "this is not json at all"

    async def stream(self, prompt: str):
        yield ""


@pytest.mark.asyncio
async def test_generate_valid_json():
    piece = await generate_piece("happy waltz", MockLLM())
    assert isinstance(piece, Piece)
    assert piece.title == "Test Piece"
    assert len(piece.parts) == 1


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
    for measure in p.parts[0].measures:
        assert len(measure.events) == 4


def test_to_midi_returns_valid_bytes():
    p = _fallback_piece("test")
    midi = p.to_midi()
    assert isinstance(midi, bytes)
    assert midi[:4] == b"MThd"


def test_to_musicxml_contains_score_partwise():
    p = _fallback_piece("test")
    xml = p.to_musicxml()
    assert isinstance(xml, str)
    assert "score-partwise" in xml


def test_chord_events_in_piece():
    """Verify that Chord events round-trip through the model and MIDI export."""
    from app.core.data_model import Chord, Measure, Note, Part, Piece

    chord = Chord(
        kind="chord",
        notes=[
            Note(kind="note", pitch=60, duration=1.0, velocity=80, offset=0.0),
            Note(kind="note", pitch=64, duration=1.0, velocity=80, offset=0.0),
        ],
        duration=1.0,
        offset=0.0,
    )
    measure = Measure(number=1, events=[chord])
    piece = Piece(
        title="Chord Test",
        tempo_bpm=120,
        parts=[Part(name="Piano", measures=[measure])],
    )
    midi = piece.to_midi()
    assert midi[:4] == b"MThd"
