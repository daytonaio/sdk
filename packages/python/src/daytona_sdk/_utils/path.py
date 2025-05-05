import os
from pathlib import PurePosixPath
from typing import Optional


def prefix_relative_path(prefix: str, path: Optional[str] = None) -> str:
    result = path
    if not result or result == "~":
        result = prefix
    elif path.startswith(prefix.lstrip("/")):
        result = path
    elif path and not PurePosixPath(path).is_absolute():
        result = os.path.join(prefix, path)
    return result
