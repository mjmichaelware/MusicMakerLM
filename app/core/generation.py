import json
import logging

from pydantic import ValidationError

from app.core.data_model import Measure, Note, Part, Piece
from app.llm.prompts import GENERATE_PIECE_SYSTEM, GENERATE_PIECE_TEMPLATE
from app.providers.base import LLMProvider, ProviderUnavailableError

logger = logging.getLogger(__name__)


def _fallback_piece(prompt: str) -> Piece:
    """Deterministic 4-bar C-major scale. Returned when LLM is unavailable or fails."""
    pitches = [60, 62, 64, 65, 67, 69, 71, 72, 72, 71, 69, 67, 65, 64, 62, 60]
    measures = []
    for bar in range(4):
        events = [
            Note(
                kind="note",
                pitch=pitches[bar * 4 + i],
                duration=1.0,
                velocity=72,
                offset=float(i),
            )
            for i in range(4)
        ]
        measures.append(Measure(number=bar + 1, events=events))
    return Piece(
        title=f"Stub: {prompt[:40]}",
        composer="MusicMakerLM (stub)",
        tempo_bpm=120.0,
        parts=[Part(name="Piano", instrument_midi=0, measures=measures)],
    )


async def generate_piece(prompt: str, provider: LLMProvider) -> Piece:
    full_prompt = GENERATE_PIECE_SYSTEM + "\n\n" + GENERATE_PIECE_TEMPLATE.format(
        user_prompt=prompt
    )
    try:
        raw = await provider.complete(full_prompt)
        # Strip any accidental markdown fences the model added
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        data = json.loads(raw)
        return Piece.model_validate(data)
    except ProviderUnavailableError as e:
        logger.warning("LLM unavailable (%s) — returning stub piece", e)
        return _fallback_piece(prompt)
    except (json.JSONDecodeError, ValidationError, KeyError, TypeError) as e:
        logger.warning("LLM returned unparseable output (%s) — returning stub piece", e)
        return _fallback_piece(prompt)
    except Exception as e:
        logger.warning("Unexpected generation error (%s) — returning stub piece", e)
        return _fallback_piece(prompt)
