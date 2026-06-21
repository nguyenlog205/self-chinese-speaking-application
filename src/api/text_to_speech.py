from fastapi import APIRouter, Query, Response, HTTPException
from src.services.tts_service import TTSService

router = APIRouter(prefix="/tts", tags=["Text-to-Speech"])
service = TTSService()


@router.get("/synthesize/")
async def synthesize_speech(
    text: str = Query(..., description="Text to synthesise."),
    speaker: str = Query("Vivian", description="Speaker name."),
    bitrate: str = Query("192k", description="MP3 bitrate."),
):
    try:
        mp3_bytes = service.synthesize(text, speaker, bitrate)
        return Response(
            content=mp3_bytes,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=output.mp3"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/speakers/")
async def list_speakers():
    return {"speakers": service.get_speakers()}