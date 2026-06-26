# TTS Core Engine Module

This module provides the core Text‑to‑Speech functionality using ChatTTS.  
It is responsible for **synthesizing speech from text** and returning **raw WAV audio bytes**, without performing any file I/O or format conversion.  

All file operations (saving, MP3 conversion, etc.) are delegated to the caller (e.g., API layer).


## 1. Overview

- **Singleton pattern** – the TTS model is loaded only once and reused across all requests.
- **Raw output** – returns WAV audio as `bytes`, ready for streaming or further processing.
- **Configurable parameters** – supports speaker selection, temperature, and speed.
- **Speaker list** – provides a list of available speakers for client‑side selection.


## 2. Class details

### 2.1. `__init__(self, compile: bool = False)`

Initialises the ChatTTS model.

- `compile`: if `True`, enables PyTorch compilation for faster inference (requires additional VRAM). Default `False`.

### 2.2. `synthesize(self, text: str, speaker: str = "default", temperature: float = 0.3, speed: int = 5) -> bytes`

Synthesises speech from the given text and returns the audio as raw WAV bytes.

| Parameter     | Type    | Default   | Description |
| :------------ | :------ | :-------- | :---------- |
| `text`        | `str`   | required  | Text to synthesise. Must not be empty. |
| `speaker`     | `str`   | `"default"` | Speaker identity. Must be one of the values returned by `get_available_speakers()`. |
| `temperature` | `float` | `0.3`     | Sampling temperature (0.0 – 1.0). Higher values produce more varied prosody. |
| `speed`       | `int`   | `5`       | Speech speed (1 – 9). `1` is slowest, `9` is fastest. |

**Returns:**  
`bytes` – the WAV audio data (24 kHz, mono).

**Raises:**  
- `ValueError` – if the input text is empty or the speaker is invalid.  
- `RuntimeError` – if the underlying TTS inference fails.

### 2.3. `get_available_speakers(self) -> List[str]`

Returns a list of all supported speaker names. The list is hardcoded based on ChatTTS capabilities and may include:

```
["default", "female_1", "female_2", "male_1", "male_2", "joyful", "sad", "angry", "calm"]
```

## 3. Configuration

The engine reads the following settings from `config/system.yml`:

| Key | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `tts.compile` | `bool` | `false` | Enable PyTorch compilation. |
| `system.log_level` | `str` | `"INFO"` | Logging level (e.g., `DEBUG`, `INFO`, `WARNING`). |

Environment variables with prefix `TTS_` can override these values (e.g., `TTS_TTS_COMPILE=true`).



## 4. Usage Example

```python
from src.core.tts_engine import get_tts_engine

engine = get_tts_engine()

# Generate WAV audio bytes
audio_bytes = engine.synthesize(
    text="你好，今天天气真好！",
    speaker="female_1",
    temperature=0.3,
    speed=6
)

# Now you can save to file, convert to MP3, stream, etc.
with open("output.wav", "wb") as f:
    f.write(audio_bytes)
```

## 5. Other technical details

### 5.1. Factory Function: `get_tts_engine(compile: Optional[bool] = None) -> TTSEngine`

Provides a singleton instance of `TTSEngine`. The model is loaded only on the first call and cached for subsequent calls.

- `compile`: if provided, overrides the configuration value. If `None`, reads from `config/system.yml`.


### 5.2. Dependencies

- `ChatTTS` – the underlying TTS model.
- `soundfile` – for writing WAV data to a memory buffer.
- `torch` – PyTorch (GPU recommended).
- `src.utils` – for configuration and logging.


### 5.3. Error Handling

- **Invalid speaker**: `ValueError` with a message listing available speakers.
- **Empty text**: `ValueError`.
- **Model inference failure**: `RuntimeError` with details from the underlying exception.

It is recommended to wrap calls to `synthesize()` in a try‑except block to handle these errors gracefully.


### 5.4.Logging

The module uses the logger named `"tts_engine"`. Logs are written to both the console and a rotating file as configured by `create_logger` in `utils.py`. All synthesis requests are logged at `DEBUG` level, while model loading and errors are logged at `INFO` or higher.
