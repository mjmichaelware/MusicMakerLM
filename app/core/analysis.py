import logging
import os
import tempfile

from app.core.data_model import Chord, Note, Piece

logger = logging.getLogger(__name__)

_SAFE_DEFAULTS = {
    "key_signature": "unknown",
    "mode": "unknown",
    "time_signature": "unknown",
    "tempo_bpm": 120.0,
    "num_measures": 0,
    "num_parts": 0,
    "note_count": 0,
    "pitch_range": {"low": 0, "high": 0},
    "chord_symbols": [],
    "roman_numeral_attempts": [],
    "warnings": [],
}


def analyze_piece(piece: Piece) -> dict:
    """Return analysis dict. Always returns all keys; never raises."""
    result: dict = {
        **_SAFE_DEFAULTS,
        "tempo_bpm": piece.tempo_bpm,
        "num_parts": len(piece.parts),
        "warnings": [],
    }

    # --- Basic stats from the Piece model (no music21 needed) ---
    try:
        all_pitches: list[int] = []
        note_count = 0
        max_measures = 0

        for part in piece.parts:
            max_measures = max(max_measures, len(part.measures))
            for measure in part.measures:
                for event in measure.events:
                    if isinstance(event, Note):
                        all_pitches.append(event.pitch)
                        note_count += 1
                    elif isinstance(event, Chord):
                        for n in event.notes:
                            all_pitches.append(n.pitch)
                        note_count += 1

        result["num_measures"] = max_measures
        result["note_count"] = note_count
        if all_pitches:
            result["pitch_range"] = {"low": min(all_pitches), "high": max(all_pitches)}

        # Time signature and tempo from first measure
        if piece.parts and piece.parts[0].measures:
            first = piece.parts[0].measures[0]
            result["time_signature"] = first.time_signature
            if first.tempo_bpm is not None:
                result["tempo_bpm"] = first.tempo_bpm

    except Exception as e:
        result["warnings"].append(f"basic stats failed: {e}")

    # --- music21 key/chord analysis (optional, wrapped) ---
    try:
        from music21 import converter

        xml_str = piece.to_musicxml()

        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = os.path.join(tmpdir, "score.musicxml")
            with open(xml_path, "w", encoding="utf-8") as f:
                f.write(xml_str)
            score = converter.parse(xml_path)

        detected_key = score.analyze("key")
        result["key_signature"] = str(detected_key)
        mode = getattr(detected_key, "mode", "unknown")
        result["mode"] = mode if mode in ("major", "minor") else "unknown"

        chord_syms, roman_nums, chord_warnings = _analyze_chords(score, detected_key)
        result["chord_symbols"] = chord_syms[:8]
        result["roman_numeral_attempts"] = roman_nums[:8]
        result["warnings"].extend(chord_warnings)

    except Exception as e:
        result["warnings"].append(f"music21 analysis failed: {e}")

    return result


def _analyze_chords(score, detected_key) -> tuple[list[str], list[str], list[str]]:
    """Return (chord_symbols, roman_numerals, warnings). Each catches its own errors."""
    from music21 import harmony

    chord_symbols: list[str] = []
    roman_numerals: list[str] = []
    warnings: list[str] = []

    try:
        from music21.chord import Chord as M21Chord

        chordified = score.chordify()
        for c in chordified.recurse().getElementsByClass(M21Chord):
            try:
                cs = harmony.chordSymbolFromChord(c)
                if cs and cs.figure:
                    chord_symbols.append(cs.figure)
            except Exception:
                pass
    except Exception as e:
        warnings.append(f"chord symbol extraction skipped: {e}")

    if chord_symbols:
        for sym in chord_symbols:
            try:
                from music21 import roman
                rn = roman.romanNumeralFromChord(
                    harmony.ChordSymbol(sym), detected_key
                )
                roman_numerals.append(str(rn.figure))
            except Exception:
                roman_numerals.append("?")
    else:
        warnings.append("chord analysis skipped: too few notes or unsupported voicing")

    return chord_symbols, roman_numerals, warnings
