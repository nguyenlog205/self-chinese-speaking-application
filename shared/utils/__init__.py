import yaml

def load_yaml_config(path: str) -> dict:
    """Đọc file YAML và trả về dict."""
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)