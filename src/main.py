from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.text_to_speech import router as tts_router
from src.api.text_analyzer import router as analyzer_router
from src.api.pronunciation import router as pronunciation_router
from src.api.vocabulary import router as vocabulary_router  # Thêm dòng này

from src.utils import load_config, create_logger

_config = load_config()
_logger = create_logger("tts_api")

app = FastAPI(
    title="TTS & Analysis & Scoring & Vocabulary API",
    version="1.0.0",
    description="Multi-service API for Chinese learning."
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(tts_router)
app.include_router(analyzer_router)
app.include_router(pronunciation_router)
app.include_router(vocabulary_router)

_logger.info("All routers registered.")


def main():
    import uvicorn
    host = _config.get("api", {}).get("host", "0.0.0.0")
    port = _config.get("api", {}).get("port", 8000)
    reload = _config.get("api", {}).get("reload", True)
    uvicorn.run("src.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()