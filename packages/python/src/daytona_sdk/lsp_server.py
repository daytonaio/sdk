"""
The Daytona SDK provides Language Server Protocol (LSP) support through Sandbox instances.
This enables advanced language features like code completion, diagnostics, and more.

Example:
    Basic LSP server usage:
    ```python
    workspace = daytona.create()
    
    # Create and start LSP server
    lsp = workspace.create_lsp_server("typescript", "/workspace/project")
    lsp.start()
    
    # Open a file for editing
    lsp.did_open("/workspace/project/src/index.ts")
    
    # Get completions at a position
    pos = Position(line=10, character=15)
    completions = lsp.completions("/workspace/project/src/index.ts", pos)
    print(f"Completions: {completions}")
    
    # Get document symbols
    symbols = lsp.document_symbols("/workspace/project/src/index.ts")
    for symbol in symbols:
        print(f"{symbol.name}: {symbol.kind}")
    
    # Clean up
    lsp.did_close("/workspace/project/src/index.ts")
    lsp.stop()
    ```

Note:
    The LSP server must be started with start() before using any other methods,
    and should be stopped with stop() when no longer needed to free resources.
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
from daytona_sdk._utils.errors import intercept_errors
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

    This class represents a zero-based position within a text document,
    specified by line number and character offset.

    Attributes:
        line (int): Zero-based line number in the document.
        character (int): Zero-based character offset on the line.
    """

    def __init__(self, line: int, character: int):
        """Initialize a new Position instance.

        Args:
            line (int): Zero-based line number in the document.
            character (int): Zero-based character offset on the line.
        """
        self.line = line
        self.character = character


class LspServer:
    """Provides Language Server Protocol functionality for code intelligence.

    This class implements a subset of the Language Server Protocol (LSP) to provide
    IDE-like features such as code completion, symbol search, and more.

    Attributes:
        language_id (LspLanguageId): The language server type (e.g., "python", "typescript").
        path_to_project (str): Absolute path to the project root directory.
        instance (WorkspaceInstance): The Sandbox instance this server belongs to.
    """

    def __init__(
        self,
        language_id: LspLanguageId,
        path_to_project: str,
        toolbox_api: ToolboxApi,
        instance: WorkspaceInstance,
    ):
        """Initializes a new LSP server instance.

        Args:
            language_id (LspLanguageId): The language server type (e.g., LspLanguageId.TYPESCRIPT).
            path_to_project (str): Absolute path to the project root directory.
            toolbox_api (ToolboxApi): API client for Sandbox operations.
            instance (WorkspaceInstance): The Sandbox instance this server belongs to.
        """
        self.language_id = str(language_id)
        self.path_to_project = path_to_project
        self.toolbox_api = toolbox_api
        self.instance = instance

    @intercept_errors(message_prefix="Failed to start LSP server: ")
    def start(self) -> None:
        """Starts the language server.

        This method must be called before using any other LSP functionality.
        It initializes the language server for the specified language and project.

        Example:
            ```python
            lsp = workspace.create_lsp_server("typescript", "/workspace/project")
            lsp.start()  # Initialize the server
            # Now ready for LSP operations
            ```
        """
        self.toolbox_api.lsp_start(
            workspace_id=self.instance.id,
            lsp_server_request=LspServerRequest(
                language_id=self.language_id,
                path_to_project=self.path_to_project,
            ),
        )

    @intercept_errors(message_prefix="Failed to stop LSP server: ")
    def stop(self) -> None:
        """Stops the language server.

        This method should be called when the LSP server is no longer needed to
        free up system resources.

        Example:
            ```python
            # When done with LSP features
            lsp.stop()  # Clean up resources
            ```
        """
        self.toolbox_api.lsp_stop(
            workspace_id=self.instance.id,
            lsp_server_request=LspServerRequest(
                language_id=self.language_id,
                path_to_project=self.path_to_project,
            ),
        )

    @intercept_errors(message_prefix="Failed to open file: ")
    def did_open(self, path: str) -> None:
        """Notifies the language server that a file has been opened.

        This method should be called when a file is opened in the editor to enable
        language features like diagnostics and completions for that file. The server
        will begin tracking the file's contents and providing language features.

        Args:
            path (str): Absolute path to the opened file.

        Example:
            ```python
            # When opening a file for editing
            lsp.did_open("/workspace/project/src/index.ts")
            # Now can get completions, symbols, etc. for this file
            ```
        """
        self.toolbox_api.lsp_did_open(
            workspace_id=self.instance.id,
            lsp_document_request=LspDocumentRequest(
                language_id=self.language_id,
                path_to_project=self.path_to_project,
                uri=f"file://{path}",
            ),
        )

    @intercept_errors(message_prefix="Failed to close file: ")
    def did_close(self, path: str) -> None:
        """Notify the language server that a file has been closed.

        This method should be called when a file is closed in the editor to allow
        the language server to clean up any resources associated with that file.
        Args:
            path (str): Absolute path to the closed file.

        Example:
            ```python
            # When done editing a file
            lsp.did_close("/workspace/project/src/index.ts")
            ```
        """
        self.toolbox_api.lsp_did_close(
            workspace_id=self.instance.id,
            lsp_document_request=LspDocumentRequest(
                language_id=self.language_id,
                path_to_project=self.path_to_project,
                uri=f"file://{path}",
            ),
        )

    @intercept_errors(message_prefix="Failed to get symbols from document: ")
    def document_symbols(self, path: str) -> List[LspSymbol]:
        """Gets symbol information from a document.

        This method returns information about all symbols (functions, classes,
        variables, etc.) defined in the specified document.

        Args:
            path (str): Absolute path to the file to get symbols from.

        Returns:
            List[LspSymbol]: List of symbols in the document. Each symbol includes:
                - name: The symbol's name
                - kind: The symbol's kind (function, class, variable, etc.)
                - location: The location of the symbol in the file

        Example:
            ```python
            # Get all symbols in a file
            symbols = lsp.document_symbols("/workspace/project/src/index.ts")
            for symbol in symbols:
                print(f"{symbol.kind} {symbol.name}: {symbol.location}")
            ```
        """
        return self.toolbox_api.lsp_document_symbols(
            workspace_id=self.instance.id,
            language_id=self.language_id,
            path_to_project=self.path_to_project,
            uri=f"file://{path}",
        )

    @intercept_errors(message_prefix="Failed to get symbols from workspace: ")
    def workspace_symbols(self, query: str) -> List[LspSymbol]:
        """Searches for symbols across the entire Sandbox.

        This method searches for symbols matching the query string across all files
        in the Sandbox. It's useful for finding declarations and definitions
        without knowing which file they're in.

        Args:
            query (str): Search query to match against symbol names.

        Returns:
            List[LspSymbol]: List of matching symbols from all files. Each symbol
                includes:
                - name: The symbol's name
                - kind: The symbol's kind (function, class, variable, etc.)
                - location: The location of the symbol in the file

        Example:
            ```python
            # Search for all symbols containing "User"
            symbols = lsp.workspace_symbols("User")
            for symbol in symbols:
                print(f"{symbol.name} in {symbol.location}")
            ```
        """
        return self.toolbox_api.lsp_workspace_symbols(
            workspace_id=self.instance.id,
            language_id=self.language_id,
            path_to_project=self.path_to_project,
            query=query,
        )

    @intercept_errors(message_prefix="Failed to get completions: ")
    def completions(self, path: str, position: Position) -> CompletionList:
        """Gets completion suggestions at a position in a file.

        Args:
            path (str): Absolute path to the file.
            position (Position): Cursor position to get completions for.

        Returns:
            CompletionList: List of completion suggestions. The list includes:
                - isIncomplete: Whether more items might be available
                - items: List of completion items, each containing:
                    - label: The text to insert
                    - kind: The kind of completion
                    - detail: Additional details about the item
                    - documentation: Documentation for the item
                    - sortText: Text used to sort the item in the list
                    - filterText: Text used to filter the item
                    - insertText: The actual text to insert (if different from label)

        Example:
            ```python
            # Get completions at a specific position
            pos = Position(line=10, character=15)
            completions = lsp.completions("/workspace/project/src/index.ts", pos)
            for item in completions.items:
                print(f"{item.label} ({item.kind}): {item.detail}")
            ```
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
