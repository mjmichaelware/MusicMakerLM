from __future__ import annotations

import json
import logging

from app.core.data_model import Measure, Note, Part, Piece
from app.llm.prompts import GENERATE_PIECE_SYSTEM, GENERATE_PIECE_TEMPLATE
from app.providers.base import LLMProvider, ProviderUnavailableError

logger = logging.getLogger(__name__)

_C_MAJOR_SCALE = [60, 62, 64, 65, 67, 69, 71, 72, 72, 71, 69, 67, 65, 64, 62, 60]


def _fallback_piece(prompt: str) -> Piece:
    """Deterministic 4-bar C-major scale — returned when the LLM is unavailable."""
    measures = []
    for bar in range(4):
        events: list = [
            Note(
                kind="note",
                pitch=_C_MAJOR_SCALE[bar * 4 + i],
                duration=1.0,
                velocity=72,
                offset=float(i),
            )
            for i in range(4)
        ]
        measures.append(Measure(number=bar + 1, events=events))
    return Piece(
        title=f"Stub: {prompt[:40]}",
        composer="MusicMakerLM (stub — LLM unavailable)",
        tempo_bpm=120.0,
        parts=[Part(name="Piano", instrument_midi=0, measures=measures)],
    )


async def generate_piece(prompt: str, provider: LLMProvider) -> Piece:
    full_prompt = (
        GENERATE_PIECE_SYSTEM
        + "\n\n"
        + GENERATE_PIECE_TEMPLATE.format(user_prompt=prompt)
    )
    try:
        raw = await provider.complete(full_prompt)
        data = json.loads(raw)
        return Piece.model_validate(data)
    except ProviderUnavailableError:
        logger.warning("LLM unavailable — returning stub piece for %r", prompt)
        return _fallback_piece(prompt)
    except (json.JSONDecodeError, Exception) as exc:
        logger.warning("LLM returned unparseable output (%s) — returning stub", exc)
        return _fallback_piece(prompt)
