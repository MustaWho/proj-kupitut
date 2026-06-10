"""Text analysis service facade."""

from app.dto.analysis import TextAnalysisRead
from app.text_analysis.integration import TextAnalyzer


class TextAnalysisService:
    """Use cases for text analysis."""

    def __init__(self, analyzer: TextAnalyzer | None = None):
        self.analyzer = analyzer or TextAnalyzer()

    async def analyze_text(self, text: str) -> TextAnalysisRead:
        result = await self.analyzer.analyze_text(text)
        return TextAnalysisRead(
            summary=result.summary,
            sentiment=result.sentiment,
            priority_score=result.priority_score,
            keywords=result.keywords,
        )
