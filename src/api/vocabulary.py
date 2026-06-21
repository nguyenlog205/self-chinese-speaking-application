"""
API routes for vocabulary lookup using CEDICT offline dictionary.
"""

from fastapi import APIRouter, Query, HTTPException
from src.services.vocabulary_service import VocabularyService

router = APIRouter(prefix="/vocabulary", tags=["Vocabulary"])


def get_service():
    """Factory function to allow mocking in tests."""
    return VocabularyService()


@router.get("/lookup/")
async def lookup_word(
    word: str = Query(..., description="Chinese word to look up (simplified or traditional).")
):
    try:
        service = get_service()
        result = service.lookup(word)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lookup-batch/")
async def lookup_batch(payload: dict):
    """
    Look up multiple Chinese words at once.
    Expects JSON: {"words": ["你好", "世界"]}
    """
    words = payload.get("words")
    if words is None:
        raise HTTPException(status_code=400, detail="Missing 'words' field")
    if not isinstance(words, list):
        raise HTTPException(status_code=400, detail="'words' must be a list")
    try:
        service = get_service()
        results = service.lookup_batch(words)
        return {"results": results}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))