import os
from pathlib import PurePosixPath
from typing import Optional


def prefix_relative_path(prefix: str, path: Optional[str] = None) -> str:
    result = prefix

    if path:
        path = path.strip()
        if path == "~":
            result = prefix
        elif path.startswith("~/"):
            result = os.path.join(prefix, path[2:])
        elif path.startswith(prefix.lstrip("/")):
            result = path
        elif not PurePosixPath(path).is_absolute():
            result = os.path.join(prefix, path)

    return result
