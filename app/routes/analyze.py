from fastapi import APIRouter
from pydantic import BaseModel

from app.core.analysis import analyze_piece
from app.core.data_model import Piece

router = APIRouter()


class AnalyzeRequest(BaseModel):
    piece_json: dict


class AnalyzeResponse(BaseModel):
    analysis: dict


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_endpoint(body: AnalyzeRequest):
    piece = Piece.model_validate(body.piece_json)
    analysis = analyze_piece(piece)
    return AnalyzeResponse(analysis=analysis)
