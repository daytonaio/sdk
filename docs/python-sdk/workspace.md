---
sidebar_label: workspace
title: workspace
---

Core workspace functionality for Daytona.

This module provides the main Workspace class that coordinates file system,
Git, process execution, and LSP functionality.

## `Workspace` Objects

```python
class Workspace()
```

Represents a Daytona workspace instance.

A workspace provides file system operations, Git operations, process execution,
and LSP functionality.

**Arguments**:

- `id` - Unique identifier for the workspace
- `instance` - The underlying workspace instance
- `toolbox_api` - API client for workspace operations
- `code_toolbox` - Language-specific toolbox implementation
  

**Attributes**:

- `fs` - File system operations interface for managing files and directories
- `git` - Git operations interface for version control functionality
- `process` - Process execution interface for running commands and code

#### `get_workspace_root_dir`

```python
def get_workspace_root_dir() -> str
```

Gets the root directory path of the workspace.

**Returns**:

  The absolute path to the workspace root

#### `create_lsp_server`

```python
def create_lsp_server(language_id: LspLanguageId,
                      path_to_project: str) -> LspServer
```

Creates a new Language Server Protocol (LSP) server instance.

**Arguments**:

- `language_id` - The language server type
- `path_to_project` - Path to the project root
  

**Returns**:

  A new LSP server instance

