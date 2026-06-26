"""
Pronunciation scoring module using CER (Character Error Rate).
Compares user's speech (via Whisper ASR) with reference text.
"""

import os
import tempfile
import functools
from typing import Dict, Any, List

import soundfile as sf
from faster_whisper import WhisperModel
from jiwer import cer

from src.utils import load_config, create_logger

_config = load_config()
_logger = create_logger(
    name="pronunciation_scorer",
    log_level=_config.get("system", {}).get("log_level", "INFO"),
)

import re

def normalize_text(text: str) -> str:
    """
    Loại bỏ dấu câu, khoảng trắng, và chuẩn hóa để so sánh.
    """
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', '', text)
    return text


@functools.lru_cache(maxsize=1)
def get_scorer(model_size: str = "tiny") -> "PronunciationScorer":
    """
    Factory function for singleton PronunciationScorer.
    """
    _logger.info(f"Initialising PronunciationScorer with model: {model_size}")
    return PronunciationScorer(model_size=model_size)


class PronunciationScorer:
    """
    CER-based pronunciation scorer using Whisper ASR.
    """

    def __init__(self, model_size: str = "tiny", device: str = "cpu"):
        """
        Args:
            model_size: "tiny" (~75MB), "base" (~150MB)
            device: "cpu" or "cuda"
        """
        self.model_size = model_size
        # int8 quantization saves RAM, runs faster on CPU
        self.model = WhisperModel(model_size, device=device, compute_type="int8")
        _logger.info(f"Whisper model '{model_size}' loaded successfully.")

    def transcribe(self, audio_bytes: bytes) -> str:
        """
        Convert audio bytes to text using Whisper.

        Args:
            audio_bytes: Raw WAV audio data.

        Returns:
            Transcribed text.
        """
        # Write bytes to temporary WAV file for Whisper
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            segments, _ = self.model.transcribe(tmp_path, language="zh", beam_size=5)
            result = "".join([seg.text for seg in segments])
            return result.strip()
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def score(self, audio_bytes: bytes, reference_text: str) -> Dict[str, Any]:
        """
        Score pronunciation by comparing ASR result with reference text using CER.

        Args:
            audio_bytes: Raw WAV audio data.
            reference_text: The correct text that was supposed to be spoken.

        Returns:
            Dict with CER (named 'wer' for backward compatibility), 0-100 score,
            transcribed text, reference, and feedback.
        """
        if not reference_text or not reference_text.strip():
            raise ValueError("Reference text cannot be empty.")

        transcribed = self.transcribe(audio_bytes)

        ref_norm = normalize_text(reference_text)
        trans_norm = normalize_text(transcribed)

        error_rate = cer(ref_norm, trans_norm)
        score_value = max(0, 100 - (error_rate * 100))
        score_value = round(score_value, 2)

        # Simple feedback based on score
        if score_value >= 90:
            feedback = "Xuất sắc! Phát âm rất chuẩn, gần như người bản xứ."
        elif score_value >= 70:
            feedback = "Tốt! Một vài lỗi nhỏ nhưng vẫn dễ hiểu."
        elif score_value >= 50:
            feedback = "Tạm được. Có một số lỗi phát âm đáng kể."
        else:
            feedback = "Cần cải thiện nhiều. Hãy nghe lại mẫu và luyện tập thêm."

        return {
            "wer": round(error_rate, 4),   # vẫn giữ tên "wer" để tương thích frontend, nhưng thực tế là CER
            "score": score_value,
            "transcribed": transcribed,
            "reference": reference_text,
            "feedback": feedback,
        }

    def score_from_file(self, audio_path: str, reference_text: str) -> Dict[str, Any]:
        """
        Score from an existing WAV file path.
        """
        with open(audio_path, "rb") as f:
            return self.score(f.read(), reference_text)

    def get_available_speakers(self) -> List[str]:
        """(placeholder for API) not used in this module."""
        return []