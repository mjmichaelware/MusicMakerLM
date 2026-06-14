from __future__ import annotations

import json

from app.llm.prompts import EXPLAIN_ANALYSIS_TEMPLATE
from app.providers.base import LLMProvider, ProviderUnavailableError


async def explain_analysis(analysis_dict: dict, provider: LLMProvider) -> str:
    prompt = EXPLAIN_ANALYSIS_TEMPLATE.format(
        analysis_json=json.dumps(analysis_dict, indent=2)
    )
    try:
        return await provider.complete(prompt)
    except ProviderUnavailableError:
        return _fallback_explanation(analysis_dict)


def _fallback_explanation(d: dict) -> str:
    key = d.get("key_signature", "an unknown key")
    ts = d.get("time_signature", "4/4")
    bpm = d.get("tempo_bpm", 120)
    measures = d.get("num_measures", 0)
    parts = d.get("num_parts", 1)
    notes = d.get("num_notes", d.get("note_count", 0))
    low = d.get("pitch_range", {}).get("low", 0)
    high = d.get("pitch_range", {}).get("high", 0)

    return (
        f"This piece is written in {key}, in {ts} time, at {bpm:.0f} BPM. "
        f"It spans {measures} measure(s) across {parts} instrument part(s), "
        f"with {notes} notes ranging from MIDI pitch {low} to {high}. "
        f"(LLM unavailable — showing deterministic summary.)"
    )
