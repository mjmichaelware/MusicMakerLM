import json
import logging

from app.llm.prompts import EXPLAIN_ANALYSIS_TEMPLATE
from app.providers.base import LLMProvider, ProviderUnavailableError

logger = logging.getLogger(__name__)


async def explain_analysis(analysis_dict: dict, provider: LLMProvider) -> str:
    prompt = EXPLAIN_ANALYSIS_TEMPLATE.format(
        analysis_json=json.dumps(analysis_dict, indent=2)
    )
    try:
        return await provider.complete(prompt)
    except ProviderUnavailableError as e:
        logger.warning("LLM unavailable for tutor explanation (%s)", e)
        return _fallback_explanation(analysis_dict)
    except Exception as e:
        logger.warning("Unexpected tutor error (%s)", e)
        return _fallback_explanation(analysis_dict)


def _fallback_explanation(d: dict) -> str:
    key = d.get("key_signature", "an unknown key")
    ts = d.get("time_signature", "4/4")
    bpm = d.get("tempo_bpm", 120)
    bars = d.get("num_measures", 0)
    parts = d.get("num_parts", 1)
    notes = d.get("note_count", 0)
    return (
        f"This piece is in {key} with a time signature of {ts} at {bpm:.0f} BPM. "
        f"It has {bars} measure(s) across {parts} part(s) with {notes} note event(s). "
        "(LLM unavailable — showing deterministic summary.)"
    )
