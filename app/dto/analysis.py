"""Text analysis schemas."""

from typing import Literal

from pydantic import Field

from app.dto.base import ORMBaseModel


class TextAnalysisRequest(ORMBaseModel):
    """Text analysis request."""

    text: str = Field(min_length=3, max_length=4000)


class TextAnalysisRead(ORMBaseModel):
    """Text analysis response."""

    summary: str
    sentiment: Literal["positive", "neutral", "negative"]
    priority_score: int = Field(ge=1, le=5)
    keywords: list[str]
