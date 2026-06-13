import pytest

from app.core.analysis import analyze_piece
from app.core.generation import _fallback_piece

REQUIRED_KEYS = {
    "key_signature",
    "mode",
    "time_signature",
    "tempo_bpm",
    "num_measures",
    "num_parts",
    "note_count",
    "pitch_range",
    "chord_symbols",
    "roman_numeral_attempts",
    "warnings",
}


def test_analyze_fallback_piece_has_all_keys():
    piece = _fallback_piece("test")
    result = analyze_piece(piece)
    assert REQUIRED_KEYS == REQUIRED_KEYS & set(result.keys()), (
        f"Missing keys: {REQUIRED_KEYS - set(result.keys())}"
    )


def test_analyze_fallback_piece_basic_stats():
    piece = _fallback_piece("test")
    result = analyze_piece(piece)
    assert result["num_measures"] == 4
    assert result["num_parts"] == 1
    assert result["note_count"] == 16
    assert result["pitch_range"]["low"] <= result["pitch_range"]["high"]


def test_analyze_pitch_range():
    piece = _fallback_piece("test")
    result = analyze_piece(piece)
    assert result["pitch_range"]["low"] >= 0
    assert result["pitch_range"]["high"] <= 127


def test_analyze_returns_lists_for_chords_and_romans():
    piece = _fallback_piece("test")
    result = analyze_piece(piece)
    assert isinstance(result["chord_symbols"], list)
    assert isinstance(result["roman_numeral_attempts"], list)


def test_analyze_warnings_always_present():
    piece = _fallback_piece("test")
    result = analyze_piece(piece)
    assert "warnings" in result
    assert isinstance(result["warnings"], list)


def test_analyze_mode_valid_value():
    piece = _fallback_piece("test")
    result = analyze_piece(piece)
    assert result["mode"] in ("major", "minor", "unknown")


def test_analyze_empty_piece_does_not_crash():
    from app.core.data_model import Piece
    empty = Piece(title="Empty", tempo_bpm=90)
    result = analyze_piece(empty)
    assert isinstance(result, dict)
    assert REQUIRED_KEYS == REQUIRED_KEYS & set(result.keys())
