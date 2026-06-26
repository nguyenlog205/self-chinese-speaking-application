"""
Text Analyzer module for Chinese language processing.

Provides:
- Tokenization (word segmentation)
- Pinyin conversion with tone marks
- Part-of-speech tagging (optional)
"""

import functools
from typing import List, Dict, Any, Optional

import jieba
import jieba.posseg as pseg
from pypinyin import pinyin, Style, lazy_pinyin

from src.utils import load_config, create_logger

_config = load_config()
_logger = create_logger(
    name="text_analyzer",
    log_level=_config.get("system", {}).get("log_level", "INFO"),
)


@functools.lru_cache(maxsize=1)
def get_analyzer() -> "TextAnalyzer":
    """
    Factory function that returns a singleton TextAnalyzer instance.
    """
    _logger.info("Initialising TextAnalyzer singleton...")
    return TextAnalyzer()


class TextAnalyzer:
    """
    Chinese text analyzer with tokenization and pinyin conversion.
    """

    def __init__(self):
        # Load jieba dictionary (optional custom dict)
        # jieba.load_userdict("custom_dict.txt")
        _logger.info("TextAnalyzer initialised.")

    def analyze(
        self,
        text: str,
        with_pos: bool = True,
        with_pinyin: bool = True,
    ) -> Dict[str, Any]:
        """
        Analyze Chinese text and return segments with pinyin and POS.

        Args:
            text: Input Chinese text.
            with_pos: Include part-of-speech tags.
            with_pinyin: Include pinyin for each segment.

        Returns:
            Dictionary with original text and list of segments.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        _logger.debug(f"Analyzing text: {text[:60]}...")

        # Tokenize using jieba with POS tags
        segments = []
        for word, flag in pseg.cut(text):
            segment = {
                "text": word,
                "pos": flag if with_pos else None,
            }

            if with_pinyin:
                # Get pinyin with tone marks (preserve tone numbers)
                pinyins = pinyin(word, style=Style.TONE, heteronym=False)
                segment["pinyin"] = " ".join([p[0] for p in pinyins])

            segments.append(segment)

        # Remove None values if not requested
        if not with_pos:
            for seg in segments:
                seg.pop("pos", None)

        return {
            "original": text,
            "segments": segments,
            "segment_count": len(segments),
        }

    def get_pinyin_plain(self, text: str) -> str:
        """
        Return plain pinyin (without tone marks) for the entire text.
        Useful for phonetic transcription without segmentation.
        """
        return " ".join(lazy_pinyin(text))

    def get_pinyin_tone(self, text: str) -> str:
        """
        Return pinyin with tone marks for the entire text.
        """
        pinyins = pinyin(text, style=Style.TONE, heteronym=False)
        return " ".join([p[0] for p in pinyins])

    def tokenize_only(self, text: str) -> List[str]:
        """
        Return only the list of tokens (words), without POS or pinyin.
        """
        return list(jieba.cut(text))