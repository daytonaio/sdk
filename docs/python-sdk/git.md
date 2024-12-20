# Table of Contents

* [git](#git)
  * [Git](#git.Git)
    * [add](#git.Git.add)
    * [branches](#git.Git.branches)
    * [clone](#git.Git.clone)
    * [commit](#git.Git.commit)
    * [push](#git.Git.push)
    * [pull](#git.Git.pull)
    * [status](#git.Git.status)

---
sidebar_label: git
title: git
---

Git operations within a Daytona workspace.

This module provides functionality for managing Git repositories, including cloning,
committing changes, pushing/pulling, and checking repository status.

## `Git` Objects

```python
class Git()
```

Provides Git operations within a workspace.

**Arguments**:

- `workspace` - The parent workspace instance
- `toolbox_api` - API client for workspace operations
- `instance` - The workspace instance

#### `add(path: str, files: List[str])`

```python
def add(path: str, files: List[str]) -> None
```

Stages files for commit.

**Arguments**:

- `path` - Repository path
- `files` - List of file paths to stage

#### `branches(path: str)`

```python
def branches(path: str) -> ListBranchResponse
```

Lists branches in the repository.

**Arguments**:

- `path` - Repository path
  

**Returns**:

  List of branches and their information

#### `clone(url: str, path: str, branch: Optional[str] = None, commit_id: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None)`

```python
def clone(url: str,
          path: str,
          branch: Optional[str] = None,
          commit_id: Optional[str] = None,
          username: Optional[str] = None,
          password: Optional[str] = None) -> None
```

Clones a Git repository.

**Arguments**:

- `url` - Repository URL
- `path` - Destination path
- `branch` - Branch to clone (optional)
- `commit_id` - Specific commit to clone (optional)
- `username` - Git username for authentication (optional)
- `password` - Git password/token for authentication (optional)

#### `commit(path: str, message: str, author: str, email: str)`

```python
def commit(path: str, message: str, author: str, email: str) -> None
```

Commits staged changes.

**Arguments**:

- `path` - Repository path
- `message` - Commit message
- `author` - Name of the commit author
- `email` - Email of the commit author

#### `push(path: str, username: Optional[str] = None, password: Optional[str] = None)`

```python
def push(path: str,
         username: Optional[str] = None,
         password: Optional[str] = None) -> None
```

Pushes local commits to the remote repository.

**Arguments**:

- `path` - Repository path
- `username` - Git username for authentication (optional)
- `password` - Git password/token for authentication (optional)

#### `pull(path: str, username: Optional[str] = None, password: Optional[str] = None)`

```python
def pull(path: str,
         username: Optional[str] = None,
         password: Optional[str] = None) -> None
```

Pulls changes from the remote repository.

**Arguments**:

- `path` - Repository path
- `username` - Git username for authentication (optional)
- `password` - Git password/token for authentication (optional)

#### `status(path: str)`

```python
def status(path: str) -> GitStatus
```

Gets the current Git repository status.

**Arguments**:

- `path` - Repository path
  

**Returns**:

  Repository status information including staged, unstaged, and untracked files

