from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.core.analysis import analyze_piece
from app.core.data_model import Piece
from app.core.tutor import explain_analysis
from app.providers.base import get_llm_provider

router = APIRouter()


class TeachRequest(BaseModel):
    piece_json: dict


class TeachResponse(BaseModel):
    analysis: dict
    explanation: str


@router.post("/teach", response_model=TeachResponse)
async def teach_endpoint(
    body: TeachRequest,
    settings: Settings = Depends(get_settings),
):
    piece = Piece.model_validate(body.piece_json)
    analysis = analyze_piece(piece)
    llm = get_llm_provider(settings)
    explanation = await explain_analysis(analysis, llm)
    return TeachResponse(analysis=analysis, explanation=explanation)
