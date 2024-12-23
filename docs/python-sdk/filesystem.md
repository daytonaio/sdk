---
sidebar_label: filesystem
title: filesystem
---

File system operations within a Daytona workspace.

This module provides functionality for managing files and directories in a workspace,
including creating, deleting, moving files, and searching file contents.

## `FileSystem` Objects

```python
class FileSystem()
```

Provides file system operations within a workspace.

**Arguments**:

- `instance` - The workspace instance
- `toolbox_api` - API client for workspace operations

#### `create_folder`

```python
def create_folder(path: str, mode: str) -> None
```

Creates a new folder in the workspace.

**Arguments**:

- `path` - Path where the folder should be created
- `mode` - Folder permissions in octal format (e.g. &quot;755&quot;)

#### `delete_file`

```python
def delete_file(path: str) -> None
```

Deletes a file from the workspace.

**Arguments**:

- `path` - Path to the file to delete

#### `download_file`

```python
def download_file(path: str) -> bytes
```

Downloads a file from the workspace.

**Arguments**:

- `path` - Path to the file to download
  

**Returns**:

  The file contents as bytes

#### `find_files`

```python
def find_files(path: str, pattern: str) -> List[Match]
```

Searches for files matching a pattern.

**Arguments**:

- `path` - Root directory to start search from
- `pattern` - Search pattern to match against file contents
  

**Returns**:

  List of matches found in files

#### `get_file_details`

```python
def get_file_details(path: str) -> FileInfo
```

Gets detailed information about a file.

**Arguments**:

- `path` - Path to the file
  

**Returns**:

  Detailed file information including size, permissions, etc.

#### `list_files`

```python
def list_files(path: str) -> List[FileInfo]
```

Lists files and directories in a given path.

**Arguments**:

- `path` - Directory path to list contents from
  

**Returns**:

  List of file and directory information

#### `move_files`

```python
def move_files(source: str, destination: str) -> None
```

Moves files from one location to another.

**Arguments**:

- `source` - Source file/directory path
- `destination` - Destination path

#### `replace_in_files`

```python
def replace_in_files(files: List[str], pattern: str,
                     new_value: str) -> List[ReplaceResult]
```

Replaces text in multiple files.

**Arguments**:

- `files` - List of file paths to perform replacements in
- `pattern` - Pattern to search for (supports regex)
- `new_value` - Text to replace matches with
  

**Returns**:

  List of results indicating replacements made in each file

#### `search_files`

```python
def search_files(path: str, pattern: str) -> SearchFilesResponse
```

Searches for files matching a pattern in their names.

**Arguments**:

- `path` - Root directory to start search from
- `pattern` - Pattern to match against file names
  

**Returns**:

  Search results containing matching file paths

#### `set_file_permissions`

```python
def set_file_permissions(path: str,
                         mode: str = None,
                         owner: str = None,
                         group: str = None) -> None
```

Sets permissions and ownership for a file or directory.

**Arguments**:

- `path` - Path to the file/directory
- `mode` - File mode/permissions in octal format (e.g. &quot;644&quot;) (optional)
- `owner` - User owner of the file (optional)
- `group` - Group owner of the file (optional)

#### `upload_file`

```python
def upload_file(path: str, file: bytes) -> None
```

Uploads a file to the workspace.

**Arguments**:

- `path` - Destination path in the workspace
- `file` - File contents as bytes

