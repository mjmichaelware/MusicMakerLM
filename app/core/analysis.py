from __future__ import annotations

import logging
import os
import tempfile

from app.core.data_model import Note, Piece

logger = logging.getLogger(__name__)

_EMPTY_ANALYSIS: dict = {
    "key_signature": "unknown",
    "mode": "unknown",
    "time_signature": "4/4",
    "tempo_bpm": 120.0,
    "num_measures": 0,
    "num_parts": 0,
    "note_count": 0,
    "pitch_range": {"low": 0, "high": 0},
    "chord_symbols": [],
    "roman_numeral_attempts": [],
    "warnings": [],
}


def _collect_pitches(piece: Piece) -> list[int]:
    pitches = []
    for part in piece.parts:
        for measure in part.measures:
            for event in measure.events:
                if isinstance(event, Note):
                    pitches.append(event.pitch)
                else:
                    pitches.extend(n.pitch for n in event.notes)
    return pitches


def analyze_piece(piece: Piece) -> dict:
    warnings: list[str] = []
    result = dict(_EMPTY_ANALYSIS)
    result["warnings"] = warnings

    all_pitches = _collect_pitches(piece)
    result["num_parts"] = len(piece.parts)
    result["num_measures"] = len(piece.parts[0].measures) if piece.parts else 0
    result["note_count"] = len(all_pitches)
    result["tempo_bpm"] = piece.tempo_bpm

    if all_pitches:
        result["pitch_range"] = {"low": min(all_pitches), "high": max(all_pitches)}
    else:
        warnings.append("No notes found — pitch range unavailable")

    if piece.parts and piece.parts[0].measures:
        result["time_signature"] = piece.parts[0].measures[0].time_signature

    try:
        xml_str = piece.to_musicxml()
        _enrich_with_music21(xml_str, result, warnings)
    except Exception as e:
        warnings.append(f"music21 analysis failed: {e}")
        logger.warning("music21 analysis error: %s", e)

    return result


def _enrich_with_music21(xml_str: str, result: dict, warnings: list[str]) -> None:
    from music21 import converter, meter
    from music21 import tempo as m21tempo

    with tempfile.NamedTemporaryFile(
        suffix=".musicxml", delete=False, mode="w", encoding="utf-8"
    ) as f:
        f.write(xml_str)
        tmp_path = f.name

    try:
        score = converter.parse(tmp_path)

        try:
            detected_key = score.analyze("key")
            result["key_signature"] = str(detected_key)
            result["mode"] = detected_key.mode
        except Exception as e:
            warnings.append(f"Key detection failed: {e}")

        try:
            ts = score.recurse().getElementsByClass(meter.TimeSignature).first()
            if ts:
                result["time_signature"] = str(ts)
        except Exception as e:
            warnings.append(f"Time signature extraction failed: {e}")

        try:
            mm = score.recurse().getElementsByClass(m21tempo.MetronomeMark).first()
            if mm:
                result["tempo_bpm"] = float(mm.number)
        except Exception as e:
            warnings.append(f"Tempo extraction failed: {e}")

        try:
            chord_symbols, roman_numerals = _chordify(score, result.get("key_signature"))
            result["chord_symbols"] = chord_symbols[:8]
            result["roman_numeral_attempts"] = roman_numerals[:8]
        except Exception as e:
            warnings.append(f"Chord analysis skipped: {e}")

    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def _chordify(score, key_sig_str: str | None) -> tuple[list[str], list[str]]:
    from music21 import harmony, roman
    from music21.chord import Chord as M21Chord

    chordified = score.chordify()
    chord_symbols: list[str] = []
    roman_numerals: list[str] = []

    detected_key = score.analyze("key")

    for c in chordified.recurse().getElementsByClass(M21Chord):
        if len(c.pitches) < 2:
            continue
        try:
            cs = harmony.chordSymbolFromChord(c)
            sym = cs.figure if cs else c.commonName
            chord_symbols.append(sym)
        except Exception:
            chord_symbols.append("?")
            roman_numerals.append("?")
            continue

        try:
            rn = roman.romanNumeralFromChord(c, detected_key)
            roman_numerals.append(str(rn.figure))
        except Exception:
            roman_numerals.append("?")

    return chord_symbols, roman_numerals
