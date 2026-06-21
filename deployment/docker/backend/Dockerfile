FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/
COPY asset ./asset
COPY logs ./logs

ENV MODEL_BASE_PATH=/app/models
ENV TTS_MODEL_PATH=/app/models/qwen-tts
ENV WHISPER_MODEL_PATH=/app/models/whisper
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "-m", "src.main"]