"""
Process and code execution within a Daytona workspace.

This module provides functionality for executing commands and running code
in the workspace environment.
"""

from typing import Optional
from api_client import (
    Workspace as WorkspaceInstance,
    WorkspaceToolboxApi,
    ExecuteResponse,
)
from .code_toolbox.workspace_python_code_toolbox import WorkspaceCodeToolbox


class Process:
    """Handles process and code execution within a workspace.
    
    Args:
        code_toolbox: Language-specific code execution toolbox
        toolbox_api: API client for workspace operations
        instance: The workspace instance
    """

    def __init__(
        self,
        code_toolbox: WorkspaceCodeToolbox,
        toolbox_api: WorkspaceToolboxApi,
        instance: WorkspaceInstance,
    ):
        self.code_toolbox = code_toolbox
        self.toolbox_api = toolbox_api
        self.instance = instance

    def exec(self, command: str, cwd: Optional[str] = None) -> ExecuteResponse:
        """Executes a shell command in the workspace.
        
        Args:
            command: Command to execute
            cwd: Working directory for command execution (optional)
            
        Returns:
            Command execution results
        """
        return self.toolbox_api.process_execute_command(
            workspace_id=self.instance.id,
            project_id="main",
            params={"command": command, "cwd": cwd},
        )

    def code_run(self, code: str) -> ExecuteResponse:
        """Executes code in the workspace using the appropriate language runtime.
        
        Args:
            code: Code to execute
            
        Returns:
            Code execution results
        """
        command = self.code_toolbox.get_run_command(code)
        return self.exec(command)
