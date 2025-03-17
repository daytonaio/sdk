from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class CodeRunParams:
    """Parameters for code execution."""

    argv: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
