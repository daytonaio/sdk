# Table of Contents

* [lsp\_server](#lsp_server)
  * [Position](#lsp_server.Position)
  * [LspServer](#lsp_server.LspServer)
    * [start](#lsp_server.LspServer.start)
    * [stop](#lsp_server.LspServer.stop)
    * [did\_open](#lsp_server.LspServer.did_open)
    * [did\_close](#lsp_server.LspServer.did_close)
    * [document\_symbols](#lsp_server.LspServer.document_symbols)
    * [workspace\_symbols](#lsp_server.LspServer.workspace_symbols)
    * [completions](#lsp_server.LspServer.completions)

---
sidebar_label: lsp_server
title: lsp_server
---

Language Server Protocol (LSP) support for Daytona workspaces.

This module provides LSP functionality for code intelligence features like
completions, symbols, and diagnostics.

## `Position` Objects

```python
class Position()
```

Represents a position in a text document.

**Arguments**:

- `line` - Zero-based line number
- `character` - Zero-based character offset

## `LspServer` Objects

```python
class LspServer()
```

Provides Language Server Protocol functionality.

**Arguments**:

- `language_id` - The language server type
- `path_to_project` - Path to the project root
- `toolbox_api` - API client for workspace operations
- `instance` - The workspace instance

#### `start()`

```python
def start() -> None
```

Starts the language server.

#### `stop()`

```python
def stop() -> None
```

Stops the language server.

Should be called when the LSP server is no longer needed to free up resources.

#### `did_open(path: str)`

```python
def did_open(path: str) -> None
```

Notifies the language server that a file has been opened.

**Arguments**:

- `path` - Path to the opened file
  
  This method should be called when a file is opened in the editor to enable
  language features like diagnostics and completions for that file.

#### `did_close(path: str)`

```python
def did_close(path: str) -> None
```

Notifies the language server that a file has been closed.

**Arguments**:

- `path` - Path to the closed file
  
  This method should be called when a file is closed in the editor to allow
  the language server to clean up any resources associated with that file.

#### `document_symbols(path: str)`

```python
def document_symbols(path: str) -> List[LspSymbol]
```

Gets symbol information from a document.

**Arguments**:

- `path` - Path to the file to get symbols from
  

**Returns**:

  List of symbols (functions, classes, variables, etc.) in the document

#### `workspace_symbols(query: str)`

```python
def workspace_symbols(query: str) -> List[LspSymbol]
```

Searches for symbols across the workspace.

**Arguments**:

- `query` - Search query to match against symbol names
  

**Returns**:

  List of matching symbols from all files in the workspace

#### `completions(path: str, position: Position)`

```python
def completions(path: str, position: Position) -> CompletionList
```

Gets completion suggestions at a position in a file.

**Arguments**:

- `path` - Path to the file
- `position` - Cursor position to get completions for
  

**Returns**:

  List of completion suggestions including items like:
  - Variable names
  - Function names
  - Class names
  - Property names
  - etc.

