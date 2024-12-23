---
sidebar_label: process
title: process
---

Process and code execution within a Daytona workspace.

This module provides functionality for executing commands and running code
in the workspace environment.

## `Process` Objects

```python
class Process()
```

Handles process and code execution within a workspace.

**Arguments**:

- `code_toolbox` - Language-specific code execution toolbox
- `toolbox_api` - API client for workspace operations
- `instance` - The workspace instance

#### `exec`

```python
def exec(command: str, cwd: Optional[str] = None) -> ExecuteResponse
```

Executes a shell command in the workspace.

**Arguments**:

- `command` - Command to execute
- `cwd` - Working directory for command execution (optional)
  

**Returns**:

  Command execution results

#### `code_run`

```python
def code_run(code: str) -> ExecuteResponse
```

Executes code in the workspace using the appropriate language runtime.

**Arguments**:

- `code` - Code to execute
  

**Returns**:

  Code execution results

