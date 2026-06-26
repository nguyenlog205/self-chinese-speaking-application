from pathlib import Path
from typing import Dict, Any, Optional
from shared.utils.config_loader import get_config
from shared.utils.file_utils import resolve_path

class CEDICTLoader:
    """
    Load và quản lý từ điển CEDICT
    """
    
    def __init__(self):
        config = get_config()
        dict_path = config.get('dictionary', {}).get('path')
        if not dict_path:
            raise ValueError("Thiếu cấu hình 'dictionary.path' trong configs/system.yml")
        
        self.cedict_path = resolve_path(dict_path)
        self._entries: Dict[str, Any] = {}
        self._loaded = False
    
    def load(self) -> Dict[str, Any]:
        """Load CEDICT từ file"""
        if not self.cedict_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file từ điển tại {self.cedict_path}")
        
        self._entries = {}
        with open(self.cedict_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.strip().split(' ')
                if len(parts) < 3:
                    continue
                traditional = parts[0]
                simplified = parts[1]
                pinyin = parts[2].strip('[]')
                definition = ' '.join(parts[3:]).strip('/')
                
                entry = {
                    'traditional': traditional,
                    'simplified': simplified,
                    'pinyin': pinyin,
                    'definition': definition
                }
                self._entries[traditional] = entry
                self._entries[simplified] = entry
        
        self._loaded = True
        return self._entries
    
    def lookup(self, word: str) -> Optional[Dict[str, Any]]:
        """Tra từ trong CEDICT"""
        if not self._loaded:
            self.load()
        return self._entries.get(word)
    
    @property
    def entries(self) -> Dict[str, Any]:
        if not self._loaded:
            self.load()
        return self._entries