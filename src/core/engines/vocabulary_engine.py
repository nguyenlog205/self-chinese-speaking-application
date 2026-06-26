"""
Vocabulary engine using CEDICT offline dictionary.
Supports mounting from an external disk volume or local directory via configuration.
"""

import os
import re
from typing import Dict, List, Optional
from pathlib import Path

from src.utils import load_config, create_logger

_config = load_config()
_vocab_config = _config.get("engines", {}).get("vocabulary_engine", {})
_logger = create_logger(
    name="vocabulary_engine",
    log_level=_config.get("system", {}).get("log_level", "INFO"),
)


class VocabularyEngine:
    """
    Offline Chinese-English dictionary lookup using CEDICT.
    Loads dictionary from a configurable mount point (base_dir).
    """

    def __init__(self, model_name: Optional[str] = None, model_dir: Optional[str] = None):
        # 1. Xác định tên thư mục model (mặc định lấy từ config hoặc fallback về "cedict")
        if model_name is None:
            model_name = _vocab_config.get("model_name_default", "cedict")

        # 2. Xử lý đường dẫn ổ đĩa mount:
        # Nếu truyền trực tiếp vào hàm thì dùng, nếu không sẽ đọc từ cấu hình hệ thống
        if model_dir is None:
            config_base_dir = _vocab_config.get("base_dir")
            if config_base_dir:
                # Chuyển đổi thành Path tuyệt đối (hỗ trợ cả đường dẫn hệ thống dạng /mnt/...)
                model_dir = Path(config_base_dir).resolve()
            else:
                # Fallback an toàn nếu file config thiếu trường base_dir
                fallback_dir = Path(__file__).resolve().parent.parent.parent.parent
                model_dir = fallback_dir / "models"
        else:
            model_dir = Path(model_dir)

        # 3. Thiết lập đường dẫn chính xác tới file dữ liệu trên ổ đĩa được mount
        self.model_path = model_dir / model_name
        self.dict_file = self.model_path / "cedict_ts.u8"

        if not self.dict_file.exists():
            raise FileNotFoundError(
                f"Dictionary file not found at mount point: {self.dict_file}. "
                f"Ensure your external storage volume is correctly mounted to the container."
            )

        _logger.info(f"Loading CEDICT from mounted path: {self.dict_file}")
        self.entries = self._load_dict()
        _logger.info(f"Loaded {len(self.entries)} entries.")

    def _load_dict(self) -> Dict[str, List[Dict]]:
        # Giữ nguyên vẹn logic đọc file bằng regex của bạn
        entries = {}
        pattern = re.compile(r'^(.+) (.+) \[(.+)\] /(.+)/$')

        with open(self.dict_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                match = pattern.match(line)
                if not match:
                    continue

                traditional = match.group(1).strip()
                simplified = match.group(2).strip()
                pinyin = match.group(3).strip()
                meanings_raw = match.group(4).strip()

                meanings = [m.strip() for m in meanings_raw.split('/') if m.strip()]

                entry = {
                    'traditional': traditional,
                    'simplified': simplified,
                    'pinyin': pinyin,
                    'meanings': meanings
                }

                if simplified not in entries:
                    entries[simplified] = []
                entries[simplified].append(entry)

                if traditional != simplified:
                    if traditional not in entries:
                        entries[traditional] = []
                    entries[traditional].append(entry)

        return entries

    def lookup(self, word: str) -> Optional[Dict]:
        if not word or not word.strip():
            raise ValueError("Word cannot be empty.")
        word = word.strip()
        found = self.entries.get(word)
        if not found:
            return None
        return {
            'word': word,
            'entries': found
        }

    def lookup_multi(self, words: List[str]) -> Dict[str, Optional[Dict]]:
        results = {}
        for w in words:
            results[w] = self.lookup(w)
        return results

    def get_available_models(self, base_dir: Optional[str] = None) -> List[str]:
        if base_dir is None:
            config_base_dir = _vocab_config.get("base_dir")
            if config_base_dir:
                base_dir = Path(config_base_dir).resolve()
            else:
                base_dir = Path(__file__).resolve().parent.parent.parent.parent / "models"
        else:
            base_dir = Path(base_dir)

        if not base_dir.exists():
            return []

        models = []
        for item in base_dir.iterdir():
            if item.is_dir() and (item / "cedict_ts.u8").exists():
                models.append(item.name)
        return models