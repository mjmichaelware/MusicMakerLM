import pytest

from app.core.analysis import analyze_piece
from app.core.generation import _fallback_piece


def test_analyze_returns_required_keys():
    piece = _fallback_piece("test")
    result = analyze_piece(piece)
    for key in ("key_signature", "mode", "time_signature", "tempo_bpm",
                "num_measures", "num_parts", "note_count", "pitch_range",
                "chord_symbols", "roman_numeral_attempts", "warnings"):
        assert key in result, f"Missing key: {key}"


def test_analyze_measure_count():
    piece = _fallback_piece("test")
    result = analyze_piece(piece)
    assert result["num_measures"] == 4


def test_analyze_pitch_range_valid():
    piece = _fallback_piece("test")
    result = analyze_piece(piece)
    assert result["pitch_range"]["low"] <= result["pitch_range"]["high"]


def test_analyze_lists_present():
    piece = _fallback_piece("test")
    result = analyze_piece(piece)
    assert isinstance(result["chord_symbols"], list)
    assert isinstance(result["roman_numeral_attempts"], list)
    assert isinstance(result["warnings"], list)


def test_analyze_does_not_raise_on_empty_piece():
    from app.core.data_model import Piece
    piece = Piece(title="Empty", parts=[])
    result = analyze_piece(piece)
    assert result["num_parts"] == 0
    assert result["note_count"] == 0
