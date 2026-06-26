"""
Vocabulary service - business logic for dictionary lookup.
"""

import logging
from src.core.engines.vocabulary_engine import VocabularyEngine

logger = logging.getLogger("vocabulary_service")


class VocabularyService:
    def __init__(self, model_name: str = "cedict"):
        self.engine = VocabularyEngine(model_name=model_name)

    def lookup(self, word: str):
        if not word or not word.strip():
            raise ValueError("Word cannot be empty.")
        result = self.engine.lookup(word.strip())
        if result is None:
            return {"word": word, "found": False, "entries": []}
        return {"word": word, "found": True, "entries": result["entries"]}

    def lookup_batch(self, words: list):
        if not words:
            raise ValueError("Words list cannot be empty.")
        results = self.engine.lookup_multi(words)
        return [
            {"word": w, "found": results[w] is not None, "entries": results[w]["entries"] if results[w] else []}
            for w in words
        ]