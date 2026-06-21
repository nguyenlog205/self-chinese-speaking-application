"""
Analysis Service - Business logic for Chinese text analysis.
Calls core text analyzer, handles validation, logging.
"""

import logging
from src.core.text_analyzer import get_analyzer

logger = logging.getLogger("analysis_service")


class AnalysisService:
    def __init__(self):
        self.analyzer = get_analyzer()

    def analyze(self, text: str, with_pos: bool = True, with_pinyin: bool = True):
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        if len(text) > 2000:
            raise ValueError("Text too long (max 2000 characters)")

        logger.info(f"Analyzing: {text[:30]}...")
        return self.analyzer.analyze(text, with_pos, with_pinyin)

    def get_pinyin(self, text: str, tone_marks: bool = True):
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        if tone_marks:
            return self.analyzer.get_pinyin_tone(text)
        return self.analyzer.get_pinyin_plain(text)

    def get_tokens(self, text: str):
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        return self.analyzer.tokenize_only(text)