# Self Chinese Speaking Application

A complete self‑hosted platform to practice Chinese pronunciation. Type or paste any Chinese text, listen to a natural‑sounding sample, record your own voice, and get an instant, objective score based on how accurately you reproduce the text.

The application combines state‑of‑the‑art Text‑to‑Speech (Qwen3‑TTS), Automatic Speech Recognition (Whisper), and Chinese text analysis (Jieba + Pypinyin) into a single, easy‑to‑run system. Everything runs locally on your own machine – your data never leaves your computer.



## 1. Overview

### 1.1. Problem Statement
Learning to pronounce Chinese correctly is difficult without a native speaker. Most existing solutions rely on cloud APIs (which require an internet connection and may incur costs) or provide generic feedback that does not pinpoint specific errors.

### 1.2. Solution
This application provides a complete offline‑capable system that:
- Generates natural Chinese speech from any text.
- Transcribes the user's voice and compares it to the reference text.
- Returns a quantitative score (0–100) and qualitative feedback.
- Runs entirely on the user's own hardware, ensuring privacy and zero recurring costs.

### 1.3. Target Audience
- Self‑learners of Chinese at HSK levels 2–5.
- Teachers who want to assign pronunciation exercises.
- Developers who need a self‑hosted TTS and pronunciation evaluation system.



## 2. Key Features

2.1. **Text‑to‑Speech Synthesis** – Convert any Chinese text into natural‑sounding MP3 audio. Supports multiple speakers with different voice characteristics.

2.2. **Pronunciation Scoring** – Record your voice, compare it to the reference text, and receive a score from 0 to 100 based on Character Error Rate (CER).

2.3. **Text Analysis** – Automatically segment Chinese text into words, display Pinyin with tone marks, and show part‑of‑speech tags.

2.4. **Real‑time Backend Status** – The frontend displays a live indicator of the backend connection (Online / Offline) so you always know if the service is ready.

2.5. **Dark / Light Theme** – Toggle between dark and light mode for comfortable viewing in any environment.

2.6. **Bilingual UI** – Switch seamlessly between Vietnamese and English for all interface text.

2.7. **Downloadable Audio** – Generated MP3 files can be saved for offline listening or sharing.


## 3. How It Works

3.1. **Text Input** – The user enters Chinese text through the web interface.

3.2. **Text Analysis** – The backend splits the text into words, generates Pinyin, and returns part‑of‑speech information.

3.3. **TTS Synthesis** – The backend uses Qwen3‑TTS (0.6B model) to produce a natural‑sounding WAV file, which is then converted to MP3 and streamed to the browser.

3.4. **Recording** – The user records their own voice using the browser's microphone. Recording automatically stops after 6 seconds.

3.5. **Scoring** – The recording is sent to the backend, where Whisper (tiny model) transcribes it. The transcription is compared to the original text using Character Error Rate (CER). The score is calculated as `max(0, 100 - CER * 100)` and returned with detailed feedback.


## 4. Technology Stack

### 4.1. Backend
- **FastAPI** – high‑performance Python web framework.
- **Qwen3‑TTS** (0.6B CustomVoice) – state‑of‑the‑art Text‑to‑Speech for Chinese.
- **Whisper** (tiny) – lightweight Automatic Speech Recognition for transcription.
- **Jieba** – Chinese word segmentation.
- **Pypinyin** – Pinyin conversion with tone marks.
- **Pydub** + **FFmpeg** – audio format conversion (WAV → MP3).

### 4.2. Frontend
- **React 18** + **TypeScript** – modern, type‑safe UI.
- **Vite** – fast development server and build tool.
- **Tailwind CSS** – utility‑first styling with dark mode support.
- **Axios** – HTTP client for API communication.
- **React Router DOM** – client‑side routing.

### 4.3. Architecture
The backend follows a clean **3‑layer architecture**:
- **Core** – pure business logic (TTS engine, text analyzer, scorer).
- **Service** – orchestrates core components, adds validation, logging, and format conversion.
- **API** – FastAPI routers that handle HTTP requests and responses.


## 5. Project Structure

```
.
├── src/                         # Backend (FastAPI)
│   ├── api/                     # API routers
│   │   ├── text_to_speech.py
│   │   ├── text_analyzer.py
│   │   └── pronunciation.py
│   ├── core/                    # Core engines
│   │   ├── tts_engine.py        # Qwen3-TTS wrapper
│   │   ├── text_analyzer.py     # Jieba + Pypinyin
│   │   └── pronunciation_scorer.py  # Whisper + CER
│   ├── services/                # Business logic layer
│   │   ├── tts_service.py
│   │   ├── analysis_service.py
│   │   └── scoring_service.py
│   ├── utils.py                 # Config & logging
│   └── main.py                  # FastAPI entry point
├── frontend/                    # React + Vite frontend
│   ├── src/
│   │   ├── components/          # Header, Footer, StatusBadge, etc.
│   │   ├── pages/               # Home, Practice, About
│   │   ├── contexts/            # Theme & Language providers
│   │   ├── hooks/               # useBackendStatus
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── config/
│   └── system.yml               # Backend configuration
├── requirements.txt
└── README.md
```



## 6. Getting Started

### 6.1. Prerequisites

- **Python 3.10+** (recommended 3.10)
- **Node.js 18+** and **npm**
- **FFmpeg** (required for audio conversion)
- **NVIDIA GPU** with at least **6 GB VRAM** (recommended for Qwen3‑TTS; CPU fallback is possible but slower)

### 6.2. Installation

**6.2.1. Clone the repository**
```bash
git clone https://github.com/nguyenlog205/self-chinese-speaking-application.git
cd self-chinese-speaking-application
```

**6.2.2. Set up the backend**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**6.2.3. Install FFmpeg**

- **Fedora**
  ```bash
  sudo dnf install ffmpeg
  ```
- **Ubuntu / Debian**
  ```bash
  sudo apt install ffmpeg
  ```

**6.2.4. Set up the frontend**
```bash
cd frontend
npm install
```

**6.2.5. Configure the backend**
Edit `config/system.yml` to adjust settings such as log level, default speaker, bitrate, and API host/port.
```yaml
system:
  log_level: INFO

tts:
  compile: false
  default_speaker: Vivian
  default_bitrate: 192k

api:
  host: 0.0.0.0
  port: 8000
  reload: true
```



## 7. Running the Application

### 7.1. Start the backend
From the project root:
```bash
python -m src.main
```
The API will be available at `http://localhost:8000`. Interactive API documentation is at `http://localhost:8000/docs`.

### 7.2. Start the frontend
In a separate terminal:
```bash
cd frontend
npm run dev
```
The frontend will be available at `http://localhost:5173`.

### 7.3. Open your browser
Navigate to `http://localhost:5173`. The application will display a live status indicator showing the backend connection.



## 8. API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/tts/synthesize/` | Generate MP3 audio from text. Parameters: `text`, `speaker`, `bitrate`. |
| `GET` | `/tts/speakers/` | List all available speaker names. |
| `GET` | `/analyze/` | Analyze Chinese text: segmentation, Pinyin, POS. |
| `GET` | `/analyze/pinyin/` | Get Pinyin (with or without tone marks). |
| `GET` | `/analyze/tokens/` | Get only the word tokens. |
| `POST` | `/pronunciation/score/` | Upload a WAV recording and get a pronunciation score. |

### 8.1. TTS Endpoint Details
**`GET /tts/synthesize/`**
- **Parameters:**
  - `text` (required) – the Chinese text to synthesise.
  - `speaker` (optional, default: `Vivian`) – voice identity.
  - `bitrate` (optional, default: `192k`) – MP3 quality.
- **Response:** MP3 audio file.
- **Error codes:**
  - `400` – invalid or empty text.
  - `500` – synthesis failed.

### 8.2. Scoring Endpoint Details
**`POST /pronunciation/score/`**
- **Parameters:**
  - `reference_text` (required) – the correct text.
- **Body:** audio file (multipart/form-data, field name `audio`).
- **Response:** JSON with `score` (0–100), `wer` (CER value), `transcribed`, `reference`, `feedback`.
- **Error codes:**
  - `400` – missing parameters.
  - `500` – scoring failed.



## 9. Usage Examples

### 9.1. Via the Web UI
1. Enter a Chinese sentence, e.g., `"大家好，中文太难了"`.
2. Click **"Phát âm"** to hear the sample.
3. Click **"Ghi âm"** and read the sentence aloud.
4. After 6 seconds, the system displays:
   - **Score** (0–100)
   - **WER** (Word Error Rate – 0.00 is perfect, 1.00 is completely wrong)
   - The transcription of your recording
   - The reference text
   - Qualitative feedback

### 9.2. Via curl

**Generate MP3**
```bash
curl "http://localhost:8000/tts/synthesize/?text=你好&speaker=Vivian&bitrate=192k" --output hello.mp3
```

**Analyze text**
```bash
curl "http://localhost:8000/analyze/?text=你好世界"
```

**Score a recording**
```bash
curl -X POST "http://localhost:8000/pronunciation/score/?reference_text=你好" \
  -F "audio=@recording.wav"
```


## 10. Configuration

All backend settings are in `config/system.yml`.

| Key | Default | Description |
| :--- | :--- | :--- |
| `system.log_level` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `tts.compile` | `false` | Enable PyTorch compilation (uses more VRAM). |
| `tts.default_speaker` | `Vivian` | Default TTS voice. |
| `tts.default_bitrate` | `192k` | Default MP3 bitrate. |
| `api.host` | `0.0.0.0` | Host to bind the server. |
| `api.port` | `8000` | Port for the API. |
| `api.reload` | `true` | Auto‑reload on code changes (development). |

Environment variables with the prefix `TTS_` override these settings, e.g. `TTS_API_PORT=9000`.



## 11. Customisation

### 11.1. Adding More Speakers
To add or change the list of available speakers, edit the `_SUPPORTED_SPEAKERS` list in `src/core/tts_engine.py`. The available voices depend on the Qwen3‑TTS model being used.

### 11.2. Changing the Whisper Model
To improve transcription accuracy, replace the Whisper model in `src/core/pronunciation_scorer.py`. Change the `model_size` parameter from `"tiny"` to `"base"`, `"small"`, or larger. Larger models require more RAM and CPU/GPU resources.

```python
scorer = PronunciationScorer(model_size="base")
```

### 11.3. Language Support
The UI supports Vietnamese and English. To add another language, extend the `translations` object in `src/contexts/LanguageContext.tsx`.



## 12. Contributing

Contributions are welcome. Please open issues or submit pull requests. For major changes, open an issue first to discuss what you would like to change.



## 13. License

This project is open‑source and available under the MIT License.



## 14. Acknowledgements

- Qwen3‑TTS – high‑quality TTS for Chinese.
- Whisper – robust speech recognition.
- FastAPI – modern Python web framework.
- React – UI library.
- Tailwind CSS – utility‑first CSS framework.
- Jieba – Chinese text segmentation.
- Pypinyin – Pinyin conversion.