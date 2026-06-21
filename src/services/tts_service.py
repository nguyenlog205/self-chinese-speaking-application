"""
TTS Service - Business logic layer for text-to-speech.
Calls core TTS engine, handles validation, format conversion, logging.
"""

import logging
from io import BytesIO
from pydub import AudioSegment
from src.core import get_tts_engine

logger = logging.getLogger("tts_service")


class TTSService:
    def __init__(self):
        self.engine = get_tts_engine()

    def synthesize(self, text: str, speaker: str = "Vivian", bitrate: str = "192k") -> bytes:
        """
        Generate MP3 audio from text.
        Returns MP3 bytes.
        """
        # 1. Validate input
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        if len(text) > 500:
            raise ValueError("Text too long (max 500 characters)")
        if speaker not in self.engine.get_available_speakers():
            logger.warning(f"Speaker '{speaker}' not available, using Vivian")
            speaker = "Vivian"

        logger.info(f"Synthesizing: {text[:30]}... (speaker={speaker})")

        # 2. Call core engine -> get WAV bytes
        wav_bytes = self.engine.synthesize(text, speaker)

        # 3. Convert WAV to MP3
        audio = AudioSegment.from_wav(BytesIO(wav_bytes))
        mp3_bytes = BytesIO()
        audio.export(mp3_bytes, format="mp3", bitrate=bitrate)
        mp3_bytes.seek(0)

        return mp3_bytes.read()

    def get_speakers(self):
        return self.engine.get_available_speakers()