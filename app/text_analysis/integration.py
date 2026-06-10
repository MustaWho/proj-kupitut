"""Deterministic text analysis used by the API."""

import re
from collections import Counter
from dataclasses import dataclass
from typing import Literal

from app.utils.exceptions import BadRequestError


Sentiment = Literal["positive", "neutral", "negative"]


@dataclass(frozen=True)
class TextAnalysisResult:
    """Structured text analysis result."""

    summary: str
    sentiment: Sentiment
    priority_score: int
    keywords: list[str]


class TextAnalyzer:
    """Small local analyzer with predictable output and no network dependency."""

    positive_words = {"good", "great", "improve", "success", "done", "stable", "fast"}
    negative_words = {"bad", "broken", "error", "fail", "blocked", "risk", "slow"}
    urgent_words = {"urgent", "critical", "deadline", "asap", "blocker", "security"}
    stop_words = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "this",
        "that",
        "need",
        "needs",
        "task",
        "project",
    }

    async def analyze_text(self, text: str) -> TextAnalysisResult:
        """Analyze text and return summary, sentiment, priority, and keywords."""

        stripped = text.strip()
        if not stripped:
            raise BadRequestError("Text must not be blank")

        words = self._words(stripped)
        sentiment = self._sentiment(words)
        priority_score = self._priority(words)
        keywords = self._keywords(words)
        summary = self._summary(stripped)
        return TextAnalysisResult(
            summary=summary,
            sentiment=sentiment,
            priority_score=priority_score,
            keywords=keywords,
        )

    def _words(self, text: str) -> list[str]:
        return re.findall(r"[a-zA-Z][a-zA-Z0-9-]{2,}", text.lower())

    def _sentiment(self, words: list[str]) -> Sentiment:
        score = sum(word in self.positive_words for word in words)
        score -= sum(word in self.negative_words for word in words)
        if score > 0:
            return "positive"
        if score < 0:
            return "negative"
        return "neutral"

    def _priority(self, words: list[str]) -> int:
        urgent_hits = sum(word in self.urgent_words for word in words)
        negative_hits = sum(word in self.negative_words for word in words)
        return min(5, max(1, 2 + urgent_hits + negative_hits))

    def _keywords(self, words: list[str]) -> list[str]:
        filtered = [word for word in words if word not in self.stop_words]
        return [word for word, _ in Counter(filtered).most_common(5)]

    def _summary(self, text: str) -> str:
        sentence = re.split(r"(?<=[.!?])\s+", text)[0]
        if len(sentence) <= 160:
            return sentence
        return f"{sentence[:157].rstrip()}..."
