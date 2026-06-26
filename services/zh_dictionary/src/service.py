from typing import Optional
from .tools.engine import CEDICTLoader
from .tools.models import WordLookupResponse

class DictionaryService:
    def __init__(self):
        self.loader = CEDICTLoader()
        # Load ngay khi khởi tạo (có thể lazy nếu muốn)
        self.loader.load()
    
    def lookup(self, word: str) -> Optional[WordLookupResponse]:
        entry = self.loader.lookup(word)
        if not entry:
            return None
        return WordLookupResponse(
            word=word,
            traditional=entry.get('traditional'),
            simplified=entry.get('simplified'),
            pinyin=entry.get('pinyin'),
            definition=entry.get('definition')
        )