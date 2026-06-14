from __future__ import annotations

import base64

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.core.generation import generate_piece
from app.core.render_audio import render_to_midi, render_to_wav
from app.core.render_notation import render_to_musicxml
from app.providers.base import get_audio_provider, get_llm_provider

router = APIRouter()


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    piece_json: dict
    musicxml: str
    midi_b64: str
    wav_b64: str | None = None


@router.post("/generate", response_model=GenerateResponse)
async def generate_endpoint(
    body: GenerateRequest,
    settings: Settings = Depends(get_settings),
):
    llm = get_llm_provider(settings)
    audio = get_audio_provider(settings)

    piece = await generate_piece(body.prompt, llm)
    midi_bytes = await render_to_midi(piece)
    wav_bytes = await render_to_wav(piece, audio, settings.soundfont_path)
    xml_str = render_to_musicxml(piece)

    return GenerateResponse(
        piece_json=piece.model_dump(),
        musicxml=xml_str,
        midi_b64=base64.b64encode(midi_bytes).decode(),
        wav_b64=base64.b64encode(wav_bytes).decode() if wav_bytes else None,
    )
