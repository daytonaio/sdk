---
sidebar_label: daytona
title: daytona
---

Daytona SDK for Python

This module provides the main entry point for interacting with Daytona Server API.

## `DaytonaConfig` Objects

```python
@dataclass
class DaytonaConfig()
```

Configuration options for initializing the Daytona client.

**Arguments**:

- `api_key` - API key for authentication with Daytona server
- `server_url` - URL of the Daytona server
- `target` - Target environment for workspaces

## `CreateWorkspaceParams` Objects

```python
@dataclass
class CreateWorkspaceParams()
```

Parameters for creating a new workspace.

**Arguments**:

- `id` - Optional workspace ID. If not provided, a random ID will be generated
- `image` - Optional Docker image to use for the workspace
- `language` - Programming language to use in the workspace

## `Daytona` Objects

```python
class Daytona()
```

#### `__init__`

```python
def __init__(config: Optional[DaytonaConfig] = None)
```

Initialize Daytona instance with optional configuration.
If no config is provided, reads from environment variables using environs.

**Arguments**:

- `config` - Optional DaytonaConfig object containing api_key, server_url, and target
  

**Raises**:

- `ValueError` - If API key or Server URL is not provided either through config or environment variables

#### `create`

```python
def create(params: Optional[CreateWorkspaceParams] = None) -> Workspace
```

Creates a new workspace.

**Arguments**:

- `params` - Parameters for workspace creation
  

**Returns**:

  The created workspace instance
  

**Raises**:

- `ValueError` - When an unsupported language is specified

#### `remove`

```python
def remove(workspace: Workspace) -> None
```

Removes a workspace.

**Arguments**:

- `workspace` - The workspace to remove

#### `get_current_workspace`

```python
def get_current_workspace() -> Workspace
```

Get the current workspace based on environment variables.

**Returns**:

- `Workspace` - The current workspace instance
  

**Raises**:

- `ValueError` - If DAYTONA_WORKSPACE_ID is not set in environment

