"""
API routes for vocabulary lookup using CEDICT offline dictionary.
"""

from fastapi import APIRouter, Query, HTTPException
from src.services.vocabulary_service import VocabularyService

router = APIRouter(prefix="/vocabulary", tags=["Vocabulary"])
service = VocabularyService()


@router.get("/lookup/")
async def lookup_word(
    word: str = Query(..., description="Chinese word to look up (simplified or traditional).")
):
    """
    Look up a Chinese word and return its meanings, pinyin, and variants.

    Example:
        GET /vocabulary/lookup/?word=你好
    """
    try:
        result = service.lookup(word)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lookup-batch/")
async def lookup_batch(
    words: list[str] = Query(..., description="List of Chinese words to look up.")
):
    """
    Look up multiple Chinese words at once.

    Example:
        POST /vocabulary/lookup-batch/?words=你好&words=世界&words=学习
    """
    try:
        results = service.lookup_batch(words)
        return {"results": results}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))