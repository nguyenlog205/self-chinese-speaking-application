from fastapi import APIRouter, Query, HTTPException
from src.services.analysis_service import AnalysisService

router = APIRouter(prefix="/analyze", tags=["Text Analysis"])
service = AnalysisService()


@router.get("/")
async def analyze_text(
    text: str = Query(..., description="Chinese text to analyze."),
    with_pos: bool = Query(True, description="Include part-of-speech tags."),
    with_pinyin: bool = Query(True, description="Include pinyin."),
):
    try:
        return service.analyze(text, with_pos, with_pinyin)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pinyin/")
async def get_pinyin(
    text: str = Query(..., description="Chinese text."),
    tone_marks: bool = Query(True, description="Include tone marks."),
):
    try:
        result = service.get_pinyin(text, tone_marks)
        return {"text": text, "pinyin": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tokens/")
async def get_tokens(
    text: str = Query(..., description="Chinese text."),
):
    try:
        tokens = service.get_tokens(text)
        return {"text": text, "tokens": tokens}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))