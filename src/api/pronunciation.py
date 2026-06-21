from fastapi import APIRouter, Query, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from src.services.scoring_service import ScoringService

router = APIRouter(prefix="/pronunciation", tags=["Pronunciation"])
service = ScoringService()


@router.post("/score/")
async def score_pronunciation(
    audio: UploadFile = File(..., description="Audio file (WAV format)"),
    reference_text: str = Query(..., description="Reference text to compare against"),
):
    try:
        audio_bytes = await audio.read()
        result = service.score(audio_bytes, reference_text)
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))