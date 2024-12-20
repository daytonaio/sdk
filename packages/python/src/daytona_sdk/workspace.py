"""
Core workspace functionality for Daytona.

This module provides the main Workspace class that coordinates file system,
Git, process execution, and LSP functionality.
"""

import asyncio
from .filesystem import FileSystem
from .git import Git
from .process import Process
from .lsp_server import LspServer, LspLanguageId
from api_client import Workspace as WorkspaceInstance, WorkspaceToolboxApi
from .code_toolbox.workspace_python_code_toolbox import WorkspaceCodeToolbox


class Workspace:
    """Represents a Daytona workspace instance.
    
    A workspace provides file system operations, Git operations, process execution,
    and LSP functionality.
    
    Args:
        id: Unique identifier for the workspace
        instance: The underlying workspace instance
        toolbox_api: API client for workspace operations
        code_toolbox: Language-specific toolbox implementation
        
    Attributes:
        fs: File system operations interface for managing files and directories
        git: Git operations interface for version control functionality
        process: Process execution interface for running commands and code
    """

    def __init__(
        self,
        id: str,
        instance: WorkspaceInstance,
        toolbox_api: WorkspaceToolboxApi,
        code_toolbox: WorkspaceCodeToolbox,
    ):
        self.id = id
        self.instance = instance
        self.toolbox_api = toolbox_api
        self.code_toolbox = code_toolbox

        # Initialize components
        self.fs = FileSystem(instance, self.toolbox_api)  # File system operations
        self.git = Git(self, self.toolbox_api, instance)  # Git operations
        self.process = Process(self.code_toolbox, self.toolbox_api, instance)  # Process execution

    def get_workspace_root_dir(self) -> str:
        """Gets the root directory path of the workspace.
        
        Returns:
            The absolute path to the workspace root
        """
        response = self.toolbox_api.get_project_dir(
            workspace_id=self.instance.id, project_id="main"
        )
        return response.dir

    def create_lsp_server(
        self, language_id: LspLanguageId, path_to_project: str
    ) -> LspServer:
        """Creates a new Language Server Protocol (LSP) server instance.
        
        Args:
            language_id: The language server type
            path_to_project: Path to the project root
            
        Returns:
            A new LSP server instance
        """
        return LspServer(language_id, path_to_project, self.toolbox_api, self.instance)
