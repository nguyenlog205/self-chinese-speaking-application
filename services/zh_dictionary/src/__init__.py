from .routes import router
from .tools.models import WordLookupResponse
from .service import DictionaryService

__all__ = ['router', 'WordLookupResponse', 'DictionaryService']