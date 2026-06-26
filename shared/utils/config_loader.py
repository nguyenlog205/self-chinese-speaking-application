import yaml
from pathlib import Path
from typing import Any, Dict

def load_config(config_path: Path = Path("configs/system.yml")) -> Dict[str, Any]:
    """Load file YAML và trả về dict"""
    if not config_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file config: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# Singleton pattern: load một lần và dùng chung
_CONFIG = None

def get_config() -> Dict[str, Any]:
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = load_config()
    return _CONFIG