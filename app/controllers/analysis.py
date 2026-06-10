"""Text analysis endpoints."""

from fastapi import APIRouter

from app.dto.analysis import TextAnalysisRead, TextAnalysisRequest
from app.services.analysis_service import TextAnalysisService

router = APIRouter()


@router.post("/analyze", response_model=TextAnalysisRead)
async def analyze_text(payload: TextAnalysisRequest) -> TextAnalysisRead:
    """Analyze arbitrary text."""

    return await TextAnalysisService().analyze_text(payload.text)
