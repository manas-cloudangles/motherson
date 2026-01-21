from pathlib import Path
from typing import Optional, Union

def read_file_safe(file_path: Union[str, Path]) -> Optional[str]:
    """Read file content safely."""
    path = Path(file_path)
    if not path.exists():
        return None
    try:
        return path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading file {path}: {e}")
        return None

def write_file_safe(file_path: Union[str, Path], content: str) -> bool:
    """Write content to file safely."""
    path = Path(file_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Error writing file {path}: {e}")
        return False
