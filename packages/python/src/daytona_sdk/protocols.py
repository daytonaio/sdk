from typing import Protocol, Dict, Any

class WorkspaceCodeToolbox(Protocol):
    def get_default_image(self) -> str: ...
    def get_code_run_command(self, code: str) -> str: ...
    def get_code_run_args(self) -> list[str]: ...
    # ... other protocol methods 

class WorkspaceInstance(Protocol):
    id: str