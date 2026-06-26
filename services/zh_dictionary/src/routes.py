from fastapi import APIRouter, Query, HTTPException
from .service import DictionaryService
from .tools.models import WordLookupResponse

router = APIRouter()
service = DictionaryService()

@router.get("/lookup/", response_model=WordLookupResponse)
async def lookup_word(word: str = Query(..., min_length=1, description="Từ cần tra")):
    """Tra từ điển Trung - Anh (CEDICT)"""
    result = service.lookup(word)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy từ '{word}' trong từ điển"
        )
    return result