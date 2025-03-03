"""
The Daytona SDK provides comprehensive file system operations through the `fs` module in Sandboxes.
You can perform various operations like listing files, creating directories, reading and writing files, and more.
This guide covers all available file system operations and best practices.

Examples:
    Basic file operations:
    ```python
    workspace = daytona.create()
    
    # Create a directory
    workspace.fs.create_folder("/workspace/data", "755")
    
    # Upload a file
    with open("local_file.txt", "rb") as f:
        content = f.read()
    workspace.fs.upload_file("/workspace/data/file.txt", content)
    
    # List directory contents
    files = workspace.fs.list_files("/workspace")
    for file in files:
        print(f"Name: {file.name}")
        print(f"Is directory: {file.is_dir}")
        print(f"Size: {file.size}")
        print(f"Modified: {file.mod_time}")
    
    # Search file contents
    matches = workspace.fs.find_files(
        path="/workspace/src",
        pattern="text-of-interest"
    )
    for match in matches:
        print(f"Absolute file path: {match.file}")
        print(f"Line number: {match.line}")
        print(f"Line content: {match.content}")
        print("\n")
    ```

    File manipulation:
    ```python
    # Move files
    workspace.fs.move_files(
        "/workspace/data/old.txt",
        "/workspace/data/new.txt"
    )
    
    # Replace text in files
    results = workspace.fs.replace_in_files(
        files=["/workspace/data/new.txt"],
        pattern="old_version",
        new_value="new_version"
    )
    
    # Set permissions
    workspace.fs.set_file_permissions(
        path="/workspace/data/script.sh",
        mode="755",
        owner="daytona"
    )
    ```

Note:
    All paths should be absolute paths within the Sandbox if not explicitly
    stated otherwise.
"""

from typing import List
from daytona_api_client import (
    FileInfo,
    Match,
    ReplaceRequest,
    ReplaceResult,
    SearchFilesResponse,
    ToolboxApi,
)
from daytona_sdk._utils.errors import intercept_errors
from .protocols import WorkspaceInstance


class FileSystem:
    """Provides file system operations within a Sandbox.

    This class implements a high-level interface to file system operations that can
    be performed within a Daytona Sandbox. It supports common operations like
    creating, deleting, and moving files, as well as searching file contents and
    managing permissions.

    Attributes:
        instance (WorkspaceInstance): The Sandbox instance this file system belongs to.
    """

    def __init__(self, instance: WorkspaceInstance, toolbox_api: ToolboxApi):
        """Initializes a new FileSystem instance.

        Args:
            instance (WorkspaceInstance): The Sandbox instance this file system belongs to.
            toolbox_api (ToolboxApi): API client for Sandbox operations.
        """
        self.instance = instance
        self.toolbox_api = toolbox_api

    @intercept_errors(message_prefix="Failed to create folder: ")
    def create_folder(self, path: str, mode: str) -> None:
        """Creates a new directory in the Sandbox.

        This method creates a new directory at the specified path with the given
        permissions.

        Args:
            path (str): Absolute path where the folder should be created.
            mode (str): Folder permissions in octal format (e.g., "755" for rwxr-xr-x).

        Example:
            ```python
            # Create a directory with standard permissions
            workspace.fs.create_folder("/workspace/data", "755")

            # Create a private directory
            workspace.fs.create_folder("/workspace/secrets", "700")
            ```
        """
        self.toolbox_api.create_folder(
            workspace_id=self.instance.id, path=path, mode=mode
        )

    @intercept_errors(message_prefix="Failed to delete file: ")
    def delete_file(self, path: str) -> None:
        """Deletes a file from the Sandbox.

        This method permanently deletes a file from the Sandbox.

        Args:
            path (str): Absolute path to the file to delete.

        Example:
            ```python
            # Delete a file
            workspace.fs.delete_file("/workspace/data/old_file.txt")
            ```
        """
        self.toolbox_api.delete_file(
            workspace_id=self.instance.id, path=path
        )

    @intercept_errors(message_prefix="Failed to download file: ")
    def download_file(self, path: str) -> bytes:
        """Downloads a file from the Sandbox.

        This method retrieves the contents of a file from the Sandbox.

        Args:
            path (str): Absolute path to the file to download.

        Returns:
            bytes: The file contents as a bytes object.

        Example:
            ```python
            # Download and save a file locally
            content = workspace.fs.download_file("/workspace/data/file.txt")
            with open("local_copy.txt", "wb") as f:
                f.write(content)

            # Download and process text content
            content = workspace.fs.download_file("/workspace/data/config.json")
            config = json.loads(content.decode('utf-8'))
            ```
        """
        return self.toolbox_api.download_file(
            workspace_id=self.instance.id, path=path
        )

    @intercept_errors(message_prefix="Failed to find files: ")
    def find_files(self, path: str, pattern: str) -> List[Match]:
        """Searches for files containing a pattern.

        This method searches file contents for a specified pattern, similar to
        the grep command.

        Args:
            path (str): Absolute path to the file or directory to search. If the path is a directory, the search will be performed recursively.
            pattern (str): Search pattern to match against file contents.

        Returns:
            List[Match]: List of matches found in files. Each Match object includes:
                - file: Path to the file containing the match
                - line: The line number where the match was found
                - content: The matching line content

        Example:
            ```python
            # Search for TODOs in Python files
            matches = workspace.fs.find_files("/workspace/src", "TODO:")
            for match in matches:
                print(f"{match.file}:{match.line}: {match.content.strip()}")
            ```
        """
        return self.toolbox_api.find_in_files(
            workspace_id=self.instance.id, path=path, pattern=pattern
        )

    @intercept_errors(message_prefix="Failed to get file info: ")
    def get_file_info(self, path: str) -> FileInfo:
        """Gets detailed information about a file.

        This method retrieves metadata about a file or directory, including its
        size, permissions, and timestamps.

        Args:
            path (str): Absolute path to the file or directory.

        Returns:
            FileInfo: Detailed file information including:
                - name: File name
                - is_dir: Whether the path is a directory
                - size: File size in bytes
                - mode: File permissions
                - mod_time: Last modification timestamp
                - permissions: File permissions in octal format
                - owner: File owner
                - group: File group

        Example:
            ```python
            # Get file metadata
            info = workspace.fs.get_file_info("/workspace/data/file.txt")
            print(f"Size: {info.size} bytes")
            print(f"Modified: {info.mod_time}")
            print(f"Mode: {info.mode}")

            # Check if path is a directory
            info = workspace.fs.get_file_info("/workspace/data")
            if info.is_dir:
                print("Path is a directory")
            ```
        """
        return self.toolbox_api.get_file_info(
            workspace_id=self.instance.id, path=path
        )

    @intercept_errors(message_prefix="Failed to list files: ")
    def list_files(self, path: str) -> List[FileInfo]:
        """Lists files and directories in a given path.

        This method returns information about all files and directories in the
        specified directory, similar to the ls -l command.

        Args:
            path (str): Absolute path to the directory to list contents from.

        Returns:
            List[FileInfo]: List of file and directory information. Each FileInfo
                object includes the same fields as described in get_file_info().

        Example:
            ```python
            # List directory contents
            files = workspace.fs.list_files("/workspace/data")

            # Print files and their sizes
            for file in files:
                if not file.is_dir:
                    print(f"{file.name}: {file.size} bytes")

            # List only directories
            dirs = [f for f in files if f.is_dir]
            print("Subdirectories:", ", ".join(d.name for d in dirs))
            ```
        """
        return self.toolbox_api.list_files(
            workspace_id=self.instance.id, path=path
        )

    @intercept_errors(message_prefix="Failed to move files: ")
    def move_files(self, source: str, destination: str) -> None:
        """Moves files from one location to another.

        This method moves or renames a file or directory. The parent directory
        of the destination must exist.

        Args:
            source (str): Absolute path to the source file or directory.
            destination (str): Absolute path to the destination.

        Example:
            ```python
            # Rename a file
            workspace.fs.move_files(
                "/workspace/data/old_name.txt",
                "/workspace/data/new_name.txt"
            )

            # Move a file to a different directory
            workspace.fs.move_files(
                "/workspace/data/file.txt",
                "/workspace/archive/file.txt"
            )

            # Move a directory
            workspace.fs.move_files(
                "/workspace/old_dir",
                "/workspace/new_dir"
            )
            ```
        """
        self.toolbox_api.move_file(
            workspace_id=self.instance.id,
            source=source,
            destination=destination,
        )

    @intercept_errors(message_prefix="Failed to replace in files: ")
    def replace_in_files(
        self, files: List[str], pattern: str, new_value: str
    ) -> List[ReplaceResult]:
        """Replaces text in multiple files.

        This method performs search and replace operations across multiple files.

        Args:
            files (List[str]): List of absolute file paths to perform replacements in.
            pattern (str): Pattern to search for.
            new_value (str): Text to replace matches with.

        Returns:
            List[ReplaceResult]: List of results indicating replacements made in
                each file. Each ReplaceResult includes:
                - file: Path to the modified file
                - success: Whether the operation was successful
                - error: Error message if the operation failed

        Example:
            ```python
            # Replace in specific files
            results = workspace.fs.replace_in_files(
                files=["/workspace/src/file1.py", "/workspace/src/file2.py"],
                pattern="old_function",
                new_value="new_function"
            )

            # Print results
            for result in results:
                if result.success:
                    print(f"{result.file}: {result.success}")
                else:
                    print(f"{result.file}: {result.error}")
            ```
        """
        replace_request = ReplaceRequest(
            files=files, new_value=new_value, pattern=pattern
        )

        return self.toolbox_api.replace_in_files(
            workspace_id=self.instance.id, replace_request=replace_request
        )

    @intercept_errors(message_prefix="Failed to search files: ")
    def search_files(self, path: str, pattern: str) -> SearchFilesResponse:
        """Searches for files and directories matching a pattern in their names.

        This method searches for files and directories whose names match the
        specified pattern. The pattern can be a simple string or a glob pattern.

        Args:
            path (str): Absolute path to the root directory to start search from.
            pattern (str): Pattern to match against file names. Supports glob
                patterns (e.g., "*.py" for Python files).

        Returns:
            SearchFilesResponse: Search results containing:
                - files: List of matching file and directory paths

        Example:
            ```python
            # Find all Python files
            result = workspace.fs.search_files("/workspace", "*.py")
            for file in result.files:
                print(file)

            # Find files with specific prefix
            result = workspace.fs.search_files("/workspace/data", "test_*")
            print(f"Found {len(result.files)} test files")
            ```
        """
        return self.toolbox_api.search_files(
            workspace_id=self.instance.id, path=path, pattern=pattern
        )

    @intercept_errors(message_prefix="Failed to set file permissions: ")
    def set_file_permissions(
        self, path: str, mode: str = None, owner: str = None, group: str = None
    ) -> None:
        """Sets permissions and ownership for a file or directory.

        This method allows changing the permissions and ownership of a file or
        directory. Any of the parameters can be None to leave that attribute
        unchanged.

        Args:
            path (str): Absolute path to the file or directory.
            mode (Optional[str]): File mode/permissions in octal format
                (e.g., "644" for rw-r--r--).
            owner (Optional[str]): User owner of the file.
            group (Optional[str]): Group owner of the file.

        Example:
            ```python
            # Make a file executable
            workspace.fs.set_file_permissions(
                path="/workspace/scripts/run.sh",
                mode="755"  # rwxr-xr-x
            )

            # Change file owner
            workspace.fs.set_file_permissions(
                path="/workspace/data/file.txt",
                owner="daytona",
                group="daytona"
            )
            ```
        """
        self.toolbox_api.set_file_permissions(
            workspace_id=self.instance.id,
            path=path,
            mode=mode,
            owner=owner,
            group=group,
        )

    @intercept_errors(message_prefix="Failed to upload file: ")
    def upload_file(self, path: str, file: bytes) -> None:
        """Uploads a file to the Sandbox.

        This method uploads a file to the specified path in the Sandbox. The
        parent directory must exist. If a file already exists at the destination
        path, it will be overwritten.

        Args:
            path (str): Absolute destination path in the Sandbox.
            file (bytes): File contents as a bytes object.

        Example:
            ```python
            # Upload a text file
            content = b"Hello, World!"
            workspace.fs.upload_file("/workspace/data/hello.txt", content)

            # Upload a local file
            with open("local_file.txt", "rb") as f:
                content = f.read()
            workspace.fs.upload_file("/workspace/data/file.txt", content)

            # Upload binary data
            import json
            data = {"key": "value"}
            content = json.dumps(data).encode('utf-8')
            workspace.fs.upload_file("/workspace/data/config.json", content)
            ```
        """
        self.toolbox_api.upload_file(
            workspace_id=self.instance.id, path=path, file=file
        )
