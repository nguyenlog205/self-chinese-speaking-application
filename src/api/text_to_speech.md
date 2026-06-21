# TTS API Router Module

This module provides the HTTP API layer for the Text‑to‑Speech service.  
It wraps the core `TTSEngine`, receives text and parameters via HTTP, synthesizes audio, converts it to MP3, and returns the file as a downloadable response.

All synthesis logic is delegated to the core module. This layer is responsible for **HTTP handling**, **MP3 conversion**, and **file management** (temporary file creation and cleanup).


## 1. Overview

- **Single endpoint** – `GET /tts/synthesize/` accepts text and synthesis parameters.
- **MP3 output** – always returns audio as MP3 (never WAV).
- **Temporary files** – creates a temporary MP3 file for download and automatically deletes it after the response is sent (via `BackgroundTasks`).
- **Speakers list** – provides `GET /tts/speakers/` endpoint to query available speakers.


## 2. Endpoints

### 2.1. `GET /tts/synthesize/`

Synthesizes speech from the provided text and returns an MP3 audio file.

**Query Parameters:**

| Parameter     | Type    | Default   | Description |
| :------------ | :------ | :-------- | :---------- |
| `text`        | `str`   | required  | Text to synthesise. Must not be empty. |
| `speaker`     | `str`   | `"default"` | Speaker identity. Must be one of the available speakers. |
| `temperature` | `float` | `0.3`     | Sampling temperature (0.0 – 1.0). |
| `bitrate`     | `str`   | `"192k"`  | MP3 bitrate (`128k`, `192k`, `320k`). |
| `speed`       | `int`   | `5`       | Speech speed (1 – 9). `1` is slowest, `9` is fastest. |

**Responses:**

| Status | Description |
| :--- | :--- |
| `200 OK` | MP3 audio file is returned as a download attachment. |
| `400 Bad Request` | Invalid input (e.g., empty text, invalid speaker). |
| `500 Internal Server Error` | TTS engine failure or conversion error. |

**Example:**

```bash
curl "http://localhost:8000/tts/synthesize/?text=你好世界&speaker=female_1&speed=7" --output speech.mp3
```

---

### 2.2. `GET /tts/speakers/`

Returns the list of available speaker names supported by the TTS engine.

**Responses:**

| Status | Description |
| :--- | :--- |
| `200 OK` | JSON object with `speakers` array. |

**Example:**

```bash
curl "http://localhost:8000/tts/speakers/"
```

**Response:**

```json
{
  "speakers": [
    "default",
    "female_1",
    "female_2",
    "male_1",
    "male_2",
    "joyful",
    "sad",
    "angry",
    "calm"
  ]
}
```

## 3. Integration

The router is designed to be included in a FastAPI application.

```python
from fastapi import FastAPI
from src.api.text_to_speech import router

app = FastAPI()
app.include_router(router)
```

Once included, the endpoints are automatically available at:
- `http://localhost:8000/tts/synthesize/`
- `http://localhost:8000/tts/speakers/`

Interactive API documentation is available at `/docs` and `/redoc`.


## 4. Error Handling

| Error | HTTP Status | Description |
| :--- | :--- | :--- |
| Empty text | `400` | Returns a `400` with detail message. |
| Invalid speaker | `400` | Returns a `400` with the list of valid speakers. |
| Engine init failure | `500` | TTS model could not be loaded. |
| Synthesis failure | `500` | Inference or conversion error. |
| MP3 conversion failure | `500` | `pydub` or `ffmpeg` error. |

All errors return a JSON object:

```json
{
  "detail": "Error description"
}
```


## 5. Usage Example

### 5.1. Start the server

```bash
python -m src.main
```

### 5.2. Synthesize speech

```bash
curl "http://localhost:8000/tts/synthesize/?text=今天天气真好&speed=6" --output output.mp3
```

### 5.3. List available speakers

```bash
curl "http://localhost:8000/tts/speakers/"
```



## 6. Other technical details

### 6.1. Dependencies

- `fastapi` – web framework.
- `uvicorn` – ASGI server.
- `pydub` – MP3 conversion (requires `ffmpeg`).
- `src.core.tts_engine` – core TTS synthesis.
- `src.utils` – configuration and logging.


### 6.2. Automatic File Cleanup

The API uses FastAPI's `BackgroundTasks` to delete the temporary MP3 file after the response is sent to the client. This prevents accumulation of temporary files in the system.

### 6.3. Logging

All synthesis requests, errors, and file operations are logged through the `"tts_engine"` logger (from the core module). The API layer itself does not create a separate logger; it relies on the core's logging.

### 6.4. MP3 Conversion

The WAV bytes from the core engine are converted to MP3 using `pydub`. The conversion requires `ffmpeg` to be installed on the system. The bitrate can be adjusted via the `bitrate` query parameter.

### 6.5. File Naming

The downloaded file is always named `output.mp3` by default. This can be customized in the `FileResponse` `filename` parameter if needed.

