from pydantic import BaseModel
from typing import Optional

class WordLookupResponse(BaseModel):
    word: str
    traditional: Optional[str] = None
    simplified: Optional[str] = None
    pinyin: Optional[str] = None
    definition: Optional[str] = None