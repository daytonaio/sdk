# Table of Contents

* [filesystem](#filesystem)
  * [FileSystem](#filesystem.FileSystem)
    * [create\_folder](#filesystem.FileSystem.create_folder)
    * [delete\_file](#filesystem.FileSystem.delete_file)
    * [download\_file](#filesystem.FileSystem.download_file)
    * [find\_files](#filesystem.FileSystem.find_files)
    * [get\_file\_details](#filesystem.FileSystem.get_file_details)
    * [list\_files](#filesystem.FileSystem.list_files)
    * [move\_files](#filesystem.FileSystem.move_files)
    * [replace\_in\_files](#filesystem.FileSystem.replace_in_files)
    * [search\_files](#filesystem.FileSystem.search_files)
    * [set\_file\_permissions](#filesystem.FileSystem.set_file_permissions)
    * [upload\_file](#filesystem.FileSystem.upload_file)

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

#### `create_folder(path: str, mode: str)`

```python
def create_folder(path: str, mode: str) -> None
```

Creates a new folder in the workspace.

**Arguments**:

- `path` - Path where the folder should be created
- `mode` - Folder permissions in octal format (e.g. &quot;755&quot;)

#### `delete_file(path: str)`

```python
def delete_file(path: str) -> None
```

Deletes a file from the workspace.

**Arguments**:

- `path` - Path to the file to delete

#### `download_file(path: str)`

```python
def download_file(path: str) -> bytes
```

Downloads a file from the workspace.

**Arguments**:

- `path` - Path to the file to download
  

**Returns**:

  The file contents as bytes

#### `find_files(path: str, pattern: str)`

```python
def find_files(path: str, pattern: str) -> List[Match]
```

Searches for files matching a pattern.

**Arguments**:

- `path` - Root directory to start search from
- `pattern` - Search pattern to match against file contents
  

**Returns**:

  List of matches found in files

#### `get_file_details(path: str)`

```python
def get_file_details(path: str) -> FileInfo
```

Gets detailed information about a file.

**Arguments**:

- `path` - Path to the file
  

**Returns**:

  Detailed file information including size, permissions, etc.

#### `list_files(path: str)`

```python
def list_files(path: str) -> List[FileInfo]
```

Lists files and directories in a given path.

**Arguments**:

- `path` - Directory path to list contents from
  

**Returns**:

  List of file and directory information

#### `move_files(source: str, destination: str)`

```python
def move_files(source: str, destination: str) -> None
```

Moves files from one location to another.

**Arguments**:

- `source` - Source file/directory path
- `destination` - Destination path

#### `replace_in_files(files: List[str], pattern: str, new_value: str)`

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

#### `search_files(path: str, pattern: str)`

```python
def search_files(path: str, pattern: str) -> SearchFilesResponse
```

Searches for files matching a pattern in their names.

**Arguments**:

- `path` - Root directory to start search from
- `pattern` - Pattern to match against file names
  

**Returns**:

  Search results containing matching file paths

#### `set_file_permissions(path: str, mode: str = None, owner: str = None, group: str = None)`

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

#### `upload_file(path: str, file: bytes)`

```python
def upload_file(path: str, file: bytes) -> None
```

Uploads a file to the workspace.

**Arguments**:

- `path` - Destination path in the workspace
- `file` - File contents as bytes

