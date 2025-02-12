"""
Language Server Protocol (LSP) support for Daytona workspaces.

This module provides LSP functionality for code intelligence features like
completions, symbols, and diagnostics.
"""
from enum import Enum
from typing import List
from daytona_api_client import (
    CompletionList,
    LspSymbol,
    ToolboxApi,
    LspServerRequest,
    LspDocumentRequest,
    LspCompletionParams
)
from daytona_sdk._utils.exceptions import intercept_exceptions
from .protocols import WorkspaceInstance


class LspLanguageId(Enum):
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"

    def __str__(self):
        return self.value
    
    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)

class Position:
    """Represents a position in a text document.
    
    Args:
        line: Zero-based line number
        character: Zero-based character offset
    """
    def __init__(self, line: int, character: int):
        self.line = line
        self.character = character


class LspServer:
    """Provides Language Server Protocol functionality.
    
    Args:
        language_id: The language server type
        path_to_project: Path to the project root
        toolbox_api: API client for workspace operations
        instance: The workspace instance
    """

    def __init__(
        self,
        language_id: LspLanguageId,
        path_to_project: str,
        toolbox_api: ToolboxApi,
        instance: WorkspaceInstance,
    ):            
        self.language_id = str(language_id)
        self.path_to_project = path_to_project
        self.toolbox_api = toolbox_api
        self.instance = instance

    @intercept_exceptions(message_prefix="Failed to start LSP server: ")
    def start(self) -> None:
        """Starts the language server."""
        self.toolbox_api.lsp_start(
            workspace_id=self.instance.id,
            lsp_server_request=LspServerRequest(
                language_id=self.language_id,
                path_to_project=self.path_to_project,
            ),
        )

    @intercept_exceptions(message_prefix="Failed to stop LSP server: ")
    def stop(self) -> None:
        """Stops the language server.
        
        Should be called when the LSP server is no longer needed to free up resources.
        """
        self.toolbox_api.lsp_stop(
            workspace_id=self.instance.id,
            lsp_server_request=LspServerRequest(
                language_id=self.language_id,
                path_to_project=self.path_to_project,
            ),
        )

    @intercept_exceptions(message_prefix="Failed to open file: ")
    def did_open(self, path: str) -> None:
        """Notifies the language server that a file has been opened.
        
        Args:
            path: Path to the opened file
            
        This method should be called when a file is opened in the editor to enable
        language features like diagnostics and completions for that file.
        """
        self.toolbox_api.lsp_did_open(
            workspace_id=self.instance.id,
            lsp_document_request=LspDocumentRequest(
                language_id=self.language_id,
                path_to_project=self.path_to_project,
                uri=f"file://{path}",
            ),
        )

    @intercept_exceptions(message_prefix="Failed to close file: ")
    def did_close(self, path: str) -> None:
        """Notifies the language server that a file has been closed.
        
        Args:
            path: Path to the closed file
            
        This method should be called when a file is closed in the editor to allow
        the language server to clean up any resources associated with that file.
        """
        self.toolbox_api.lsp_did_close(
            workspace_id=self.instance.id,
            lsp_document_request=LspDocumentRequest(
                language_id=self.language_id,
                path_to_project=self.path_to_project,
                uri=f"file://{path}",
            ),
        )

    @intercept_exceptions(message_prefix="Failed to get symbols from document: ")
    def document_symbols(self, path: str) -> List[LspSymbol]:
        """Gets symbol information from a document.
        
        Args:
            path: Path to the file to get symbols from
            
        Returns:
            List of symbols (functions, classes, variables, etc.) in the document
        """
        return self.toolbox_api.lsp_document_symbols(
            workspace_id=self.instance.id,
            language_id=self.language_id,
            path_to_project=self.path_to_project,
            uri=f"file://{path}",
        )

    @intercept_exceptions(message_prefix="Failed to get symbols from workspace: ")
    def workspace_symbols(self, query: str) -> List[LspSymbol]:
        """Searches for symbols across the workspace.
        
        Args:
            query: Search query to match against symbol names
            
        Returns:
            List of matching symbols from all files in the workspace
        """
        return self.toolbox_api.lsp_workspace_symbols(
            workspace_id=self.instance.id,
            language_id=self.language_id,
            path_to_project=self.path_to_project,
            query=query,
        )

    @intercept_exceptions(message_prefix="Failed to get completions: ")
    def completions(self, path: str, position: Position) -> CompletionList:
        """Gets completion suggestions at a position in a file.
        
        Args:
            path: Path to the file
            position: Cursor position to get completions for
            
        Returns:
            List of completion suggestions including items like:
            - Variable names
            - Function names
            - Class names
            - Property names
            - etc.
        """
        return self.toolbox_api.lsp_completions(
            workspace_id=self.instance.id,
            lsp_completion_params=LspCompletionParams(
                language_id=self.language_id,
                path_to_project=self.path_to_project,
                uri=f"file://{path}",
                position=position,
            ),
        )
