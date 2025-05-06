from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Callable, List

from daytona_api_client import (
    FileInfo,
    Match,
    ReplaceRequest,
    ReplaceResult,
    SearchFilesResponse,
    ToolboxApi,
)
from daytona_sdk._utils.errors import intercept_errors
from daytona_sdk._utils.path import prefix_relative_path

from .protocols import SandboxInstance


@dataclass
class FileUpload:
    """Represents a file to be uploaded to the Sandbox.

    Attributes:
        path (str): Absolute destination path in the Sandbox.
        content (bytes): File contents as a bytes object.
    """

    path: str
    content: bytes


class FileSystem:
    """Provides file system operations within a Sandbox.

    This class implements a high-level interface to file system operations that can
    be performed within a Daytona Sandbox.

    Attributes:
        instance (SandboxInstance): The Sandbox instance this file system belongs to.
    """

    def __init__(
        self,
        instance: SandboxInstance,
        toolbox_api: ToolboxApi,
        get_root_dir: Callable[[], str],
    ):
        """Initializes a new FileSystem instance.

        Args:
            instance (SandboxInstance): The Sandbox instance this file system belongs to.
            toolbox_api (ToolboxApi): API client for Sandbox operations.
            get_root_dir (Callable[[], str]): A function to get the default root directory of the Sandbox.
        """
        self.instance = instance
        self.toolbox_api = toolbox_api
        self._get_root_dir = get_root_dir

    @intercept_errors(message_prefix="Failed to create folder: ")
    def create_folder(self, path: str, mode: str) -> None:
        """Creates a new directory in the Sandbox at the specified path with the given
        permissions.

        Args:
            path (str): Path where the folder should be created. Relative paths are resolved based
            on the user's root directory.
            mode (str): Folder permissions in octal format (e.g., "755" for rwxr-xr-x).

        Example:
            ```python
            # Create a directory with standard permissions
            sandbox.fs.create_folder("workspace/data", "755")

            # Create a private directory
            sandbox.fs.create_folder("workspace/secrets", "700")
            ```
        """
        self.toolbox_api.create_folder(
            self.instance.id,
            path=prefix_relative_path(self._get_root_dir(), path),
            mode=mode,
        )

    @intercept_errors(message_prefix="Failed to delete file: ")
    def delete_file(self, path: str) -> None:
        """Deletes a file from the Sandbox.

        Args:
            path (str): Absolute path to the file to delete.

        Example:
            ```python
            # Delete a file
            sandbox.fs.delete_file("workspace/data/old_file.txt")
            ```
        """
        self.toolbox_api.delete_file(
            self.instance.id, path=prefix_relative_path(self._get_root_dir(), path)
        )

    @intercept_errors(message_prefix="Failed to download file: ")
    def download_file(self, path: str) -> bytes:
        """Downloads a file from the Sandbox.

        Args:
            path (str): Path to the file to download. Relative paths are resolved based on the user's
            root directory.

        Returns:
            bytes: The file contents as a bytes object.

        Example:
            ```python
            # Download and save a file locally
            content = sandbox.fs.download_file("workspace/data/file.txt")
            with open("local_copy.txt", "wb") as f:
                f.write(content)

            # Download and process text content
            content = sandbox.fs.download_file("workspace/data/config.json")
            config = json.loads(content.decode('utf-8'))
            ```
        """
        return self.toolbox_api.download_file(
            self.instance.id, path=prefix_relative_path(self._get_root_dir(), path)
        )

    @intercept_errors(message_prefix="Failed to find files: ")
    def find_files(self, path: str, pattern: str) -> List[Match]:
        """Searches for files containing a pattern, similar to
        the grep command.

        Args:
            path (str): Path to the file or directory to search. If the path is a directory,
                the search will be performed recursively. Relative paths are resolved based on the user's
                root directory.
            pattern (str): Search pattern to match against file contents.

        Returns:
            List[Match]: List of matches found in files. Each Match object includes:
                - file: Path to the file containing the match
                - line: The line number where the match was found
                - content: The matching line content

        Example:
            ```python
            # Search for TODOs in Python files
            matches = sandbox.fs.find_files("workspace/src", "TODO:")
            for match in matches:
                print(f"{match.file}:{match.line}: {match.content.strip()}")
            ```
        """
        return self.toolbox_api.find_in_files(
            self.instance.id,
            path=prefix_relative_path(self._get_root_dir(), path),
            pattern=pattern,
        )

    @intercept_errors(message_prefix="Failed to get file info: ")
    def get_file_info(self, path: str) -> FileInfo:
        """Gets detailed information about a file or directory, including its
        size, permissions, and timestamps.

        Args:
            path (str): Path to the file or directory. Relative paths are resolved based on the user's
            root directory.

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
            info = sandbox.fs.get_file_info("workspace/data/file.txt")
            print(f"Size: {info.size} bytes")
            print(f"Modified: {info.mod_time}")
            print(f"Mode: {info.mode}")

            # Check if path is a directory
            info = sandbox.fs.get_file_info("workspace/data")
            if info.is_dir:
                print("Path is a directory")
            ```
        """
        return self.toolbox_api.get_file_info(
            self.instance.id, path=prefix_relative_path(self._get_root_dir(), path)
        )

    @intercept_errors(message_prefix="Failed to list files: ")
    def list_files(self, path: str) -> List[FileInfo]:
        """Lists files and directories in a given path and returns their information, similar to the ls -l command.

        Args:
            path (str): Path to the directory to list contents from. Relative paths are resolved based on the user's
            root directory.

        Returns:
            List[FileInfo]: List of file and directory information. Each FileInfo
            object includes the same fields as described in get_file_info().

        Example:
            ```python
            # List directory contents
            files = sandbox.fs.list_files("workspace/data")

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
            self.instance.id, path=prefix_relative_path(self._get_root_dir(), path)
        )

    @intercept_errors(message_prefix="Failed to move files: ")
    def move_files(self, source: str, destination: str) -> None:
        """Moves or renames a file or directory. The parent directory of the destination must exist.

        Args:
            source (str): Path to the source file or directory. Relative paths are resolved based on the user's
            root directory.
            destination (str): Path to the destination. Relative paths are resolved based on the user's
            root directory.

        Example:
            ```python
            # Rename a file
            sandbox.fs.move_files(
                "workspace/data/old_name.txt",
                "workspace/data/new_name.txt"
            )

            # Move a file to a different directory
            sandbox.fs.move_files(
                "workspace/data/file.txt",
                "workspace/archive/file.txt"
            )

            # Move a directory
            sandbox.fs.move_files(
                "workspace/old_dir",
                "workspace/new_dir"
            )
            ```
        """
        self.toolbox_api.move_file(
            self.instance.id,
            source=prefix_relative_path(self._get_root_dir(), source),
            destination=prefix_relative_path(self._get_root_dir(), destination),
        )

    @intercept_errors(message_prefix="Failed to replace in files: ")
    def replace_in_files(
        self, files: List[str], pattern: str, new_value: str
    ) -> List[ReplaceResult]:
        """Performs search and replace operations across multiple files.

        Args:
            files (List[str]): List of file paths to perform replacements in. Relative paths are
            resolved based on the user's
            root directory.
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
            results = sandbox.fs.replace_in_files(
                files=["workspace/src/file1.py", "workspace/src/file2.py"],
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
        for i, file in enumerate(files):
            files[i] = prefix_relative_path(self._get_root_dir(), file)

        replace_request = ReplaceRequest(
            files=files, new_value=new_value, pattern=pattern
        )

        return self.toolbox_api.replace_in_files(
            self.instance.id, replace_request=replace_request
        )

    @intercept_errors(message_prefix="Failed to search files: ")
    def search_files(self, path: str, pattern: str) -> SearchFilesResponse:
        """Searches for files and directories whose names match the
        specified pattern. The pattern can be a simple string or a glob pattern.

        Args:
            path (str): Path to the root directory to start search from. Relative paths are resolved based on the user's
            root directory.
            pattern (str): Pattern to match against file names. Supports glob
                patterns (e.g., "*.py" for Python files).

        Returns:
            SearchFilesResponse: Search results containing:
                - files: List of matching file and directory paths

        Example:
            ```python
            # Find all Python files
            result = sandbox.fs.search_files("workspace", "*.py")
            for file in result.files:
                print(file)

            # Find files with specific prefix
            result = sandbox.fs.search_files("workspace/data", "test_*")
            print(f"Found {len(result.files)} test files")
            ```
        """
        return self.toolbox_api.search_files(
            self.instance.id,
            path=prefix_relative_path(self._get_root_dir(), path),
            pattern=pattern,
        )

    @intercept_errors(message_prefix="Failed to set file permissions: ")
    def set_file_permissions(
        self, path: str, mode: str = None, owner: str = None, group: str = None
    ) -> None:
        """Sets permissions and ownership for a file or directory. Any of the parameters can be None
        to leave that attribute unchanged.

        Args:
            path (str): Path to the file or directory. Relative paths are resolved based on the user's
            root directory.
            mode (Optional[str]): File mode/permissions in octal format
                (e.g., "644" for rw-r--r--).
            owner (Optional[str]): User owner of the file.
            group (Optional[str]): Group owner of the file.

        Example:
            ```python
            # Make a file executable
            sandbox.fs.set_file_permissions(
                path="workspace/scripts/run.sh",
                mode="755"  # rwxr-xr-x
            )

            # Change file owner
            sandbox.fs.set_file_permissions(
                path="workspace/data/file.txt",
                owner="daytona",
                group="daytona"
            )
            ```
        """
        self.toolbox_api.set_file_permissions(
            self.instance.id,
            path=prefix_relative_path(self._get_root_dir(), path),
            mode=mode,
            owner=owner,
            group=group,
        )

    @intercept_errors(message_prefix="Failed to upload file: ")
    def upload_file(self, path: str, file: bytes) -> None:
        """Uploads a file to the specified path in the Sandbox. The
        parent directory must exist. If a file already exists at the destination
        path, it will be overwritten.

        Args:
            path (str): Path to the destination file. Relative paths are resolved based on the user's
            root directory.
            file (bytes): File contents as a bytes object.

        Example:
            ```python
            # Upload a text file
            content = b"Hello, World!"
            sandbox.fs.upload_file("workspace/data/hello.txt", content)

            # Upload a local file
            with open("local_file.txt", "rb") as f:
                content = f.read()
            sandbox.fs.upload_file("workspace/data/file.txt", content)

            # Upload binary data
            import json
            data = {"key": "value"}
            content = json.dumps(data).encode('utf-8')
            sandbox.fs.upload_file("workspace/data/config.json", content)
            ```
        """
        self.toolbox_api.upload_file(
            self.instance.id,
            path=prefix_relative_path(self._get_root_dir(), path),
            file=file,
        )

    @intercept_errors(message_prefix="Failed to upload files: ")
    def upload_files(self, files: List[FileUpload]) -> None:
        """Uploads multiple files to the Sandbox. The parent directories must exist.
        If files already exist at the destination paths, they will be overwritten.

        Args:
            files (List[FileUpload]): List of files to upload. Each FileUpload object includes:
                - path: Path to the destination file. Relative paths are resolved based on the user's
                root directory.
                - content: File contents as a bytes object.

        Example:
            ```python
            # Upload multiple text files
            files = [
                FileUpload(
                    path="workspace/data/file1.txt",
                    content=b"Content of file 1"
                ),
                FileUpload(
                    path="workspace/data/file2.txt",
                    content=b"Content of file 2"
                ),
                FileUpload(
                    path="workspace/config/settings.json",
                    content=b'{"key": "value"}'
                )
            ]
            sandbox.fs.upload_files(files)
            ```
        """
        for file in files:
            file.path = prefix_relative_path(self._get_root_dir(), file.path)

        def upload_file(file: FileUpload) -> None:
            self.toolbox_api.upload_file(
                self.instance.id, path=file.path, file=file.content
            )

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(upload_file, file) for file in files]
            for future in futures:
                future.result()
