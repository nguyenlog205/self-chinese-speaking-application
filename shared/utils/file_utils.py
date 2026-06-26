from pathlib import Path
from typing import Union

def get_project_root() -> Path:
    """
    Trả về đường dẫn thư mục gốc của project
    """
    return Path(__file__).parent.parent.parent

def resolve_path(relative_path: Union[str, Path]) -> Path:
    """
    Chuyển đường dẫn tương đối thành đường dẫn tuyệt đối từ gốc project
    """
    return get_project_root() / relative_path