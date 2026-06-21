"""
Scoring Service - Business logic for pronunciation scoring.
Calls core pronunciation scorer, handles validation, logging.
"""

import logging
from src.core.pronunciation_scorer import get_scorer

logger = logging.getLogger("scoring_service")


class ScoringService:
    def __init__(self):
        self.scorer = get_scorer()

    def score(self, audio_bytes: bytes, reference_text: str):
        if not audio_bytes:
            raise ValueError("Audio data is empty")
        if not reference_text or not reference_text.strip():
            raise ValueError("Reference text cannot be empty")
        if len(reference_text) > 200:
            raise ValueError("Reference text too long (max 200 characters)")

        logger.info(f"Scoring: '{reference_text[:30]}...' (audio size: {len(audio_bytes)} bytes)")
        return self.scorer.score(audio_bytes, reference_text)