"""
TTS engine module using Qwen3-TTS.
Provides raw audio synthesis only, no file I/O.
"""

import io
import functools
from typing import Optional, List

import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel
from src.utils import load_config, create_logger

_config = load_config()
_logger = create_logger(
    name="tts_engine",
    log_level=_config.get("system", {}).get("log_level", "INFO"),
)


@functools.lru_cache(maxsize=1)
def get_tts_engine(compile: Optional[bool] = None) -> "TTSEngine":
    """
    Factory function that returns a singleton TTSEngine instance.
    Model loaded only once and cached.
    """
    _logger.info("Initialising TTSEngine singleton with Qwen3-TTS...")
    return TTSEngine()


class TTSEngine:
    """
    Qwen3-TTS wrapper for text-to-speech synthesis.
    """

    # Danh sách giọng có sẵn cho model 0.6B CustomVoice
    _SUPPORTED_SPEAKERS = [
        "Vivian",
        "Serena",
        "Uncle_Fu",
        "Dylan",
        "Eric",
        "Ryan",
        "Aiden",
        "Ono_Anna",
        "Sohee",
    ]

    def __init__(self):
        """
        Initialise the Qwen3-TTS engine.
        """
        _logger.info("Loading Qwen3-TTS model (0.6B)...")
        try:
            # Mặc định thử dùng flash-attn nếu có, nếu không sẽ tự fallback
            self.model = Qwen3TTSModel.from_pretrained(
                "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
                device_map="cuda:0",
                dtype=torch.bfloat16,
                attn_implementation="flash_attention_2", 
            )
        except Exception as e:
            _logger.warning(f"Flash-attn not available or failed: {e}. Falling back to default.")
            try:
                self.model = Qwen3TTSModel.from_pretrained(
                    "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
                    device_map="cuda:0",
                    dtype=torch.bfloat16,
                )
            except Exception as e2:
                _logger.error(f"Qwen3-TTS model loading failed: {e2}")
                raise RuntimeError(f"Model loading failed: {e2}") from e2

        _logger.info("Qwen3-TTS model loaded successfully.")

    def synthesize(
        self,
        text: str,
        speaker: str = "Vivian",
        temperature: float = 0.3,
        speed: int = 5,
    ) -> bytes:
        """
        Synthesize speech from text and return raw WAV bytes.

        Args:
            text: Input text to synthesize.
            speaker: Speaker identity.
            temperature: Sampling temperature (Not directly supported in Qwen's custom voice API).
            speed: Speech speed (Not directly supported in Qwen's custom voice API).

        Returns:
            Raw WAV audio data as bytes.

        Raises:
            ValueError: If text is empty.
            RuntimeError: If synthesis fails.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        if speaker not in self._SUPPORTED_SPEAKERS:
            _logger.warning(f"Speaker '{speaker}' not in list. Using 'Vivian'.")
            speaker = "Vivian"

        _logger.debug(f"Synthesising: {text[:60]}... (speaker={speaker})")

        try:
            # Qwen3-TTS generate
            wavs, sr = self.model.generate_custom_voice(
                text=text,
                language="Chinese",
                speaker=speaker,
                instruct="dùng giọng tự nhiên, rõ ràng",  # Hướng dẫn ngữ điệu
            )
        except Exception as e:
            _logger.error(f"Qwen3-TTS inference failed: {e}")
            raise RuntimeError(f"TTS synthesis failed: {e}") from e

        buffer = io.BytesIO()
        sf.write(buffer, wavs[0], sr, format="wav")
        buffer.seek(0)
        return buffer.read()

    def get_available_speakers(self) -> List[str]:
        """Return list of supported speaker names."""
        return self._SUPPORTED_SPEAKERS.copy()