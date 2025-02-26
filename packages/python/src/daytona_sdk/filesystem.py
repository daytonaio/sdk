"""
File system operations within a Daytona workspace.

This module provides functionality for managing files and directories in a workspace,
including creating, deleting, moving files, and searching file contents.
"""

from typing import List
from daytona_api_client import (
    FileInfo,
    Match,
    ReplaceRequest,
    ReplaceResult,
    SearchFilesResponse,
    Workspace as WorkspaceInstance,
    ToolboxApi,
)
from daytona_sdk._utils.exceptions import intercept_exceptions


class FileSystem:
    """Provides file system operations within a workspace.
    
    Args:
        instance: The workspace instance
        toolbox_api: API client for workspace operations
    """

    def __init__(self, instance: WorkspaceInstance, toolbox_api: ToolboxApi):
        self.instance = instance
        self.toolbox_api = toolbox_api

    @intercept_exceptions(message_prefix="Failed to create folder: ")
    def create_folder(self, path: str, mode: str) -> None:
        """Creates a new folder in the workspace.
        
        Args:
            path: Path where the folder should be created
            mode: Folder permissions in octal format (e.g. "755")
        """
        self.toolbox_api.create_folder(
            workspace_id=self.instance.id, path=path, mode=mode
        )

    @intercept_exceptions(message_prefix="Failed to delete file: ")
    def delete_file(self, path: str) -> None:
        """Deletes a file from the workspace.
        
        Args:
            path: Path to the file to delete
        """
        self.toolbox_api.delete_file(
            workspace_id=self.instance.id, path=path
        )

    @intercept_exceptions(message_prefix="Failed to download file: ")
    def download_file(self, path: str) -> bytes:
        """Downloads a file from the workspace.
        
        Args:
            path: Path to the file to download
            
        Returns:
            The file contents as bytes
        """
        return self.toolbox_api.download_file(
            workspace_id=self.instance.id, path=path
        )

    @intercept_exceptions(message_prefix="Failed to find files: ")
    def find_files(self, path: str, pattern: str) -> List[Match]:
        """Searches for files matching a pattern.
        
        Args:
            path: Root directory to start search from
            pattern: Search pattern to match against file contents
            
        Returns:
            List of matches found in files
        """
        return self.toolbox_api.find_in_files(
            workspace_id=self.instance.id, path=path, pattern=pattern
        )

    @intercept_exceptions(message_prefix="Failed to get file info: ")
    def get_file_info(self, path: str) -> FileInfo:
        """Gets detailed information about a file.
        
        Args:
            path: Path to the file
            
        Returns:
            Detailed file information including size, permissions, etc.
        """
        return self.toolbox_api.get_file_info(
            workspace_id=self.instance.id, path=path
        )

    @intercept_exceptions(message_prefix="Failed to list files: ")
    def list_files(self, path: str) -> List[FileInfo]:
        """Lists files and directories in a given path.
        
        Args:
            path: Directory path to list contents from
            
        Returns:
            List of file and directory information
        """
        return self.toolbox_api.list_files(
            workspace_id=self.instance.id, path=path
        )

    @intercept_exceptions(message_prefix="Failed to move files: ")
    def move_files(self, source: str, destination: str) -> None:
        """Moves files from one location to another.
        
        Args:
            source: Source file/directory path
            destination: Destination path
        """
        self.toolbox_api.move_file(
            workspace_id=self.instance.id,
            source=source,
            destination=destination,
        )

    @intercept_exceptions(message_prefix="Failed to replace in files: ")
    def replace_in_files(
        self, files: List[str], pattern: str, new_value: str
    ) -> List[ReplaceResult]:
        """Replaces text in multiple files.
        
        Args:
            files: List of file paths to perform replacements in
            pattern: Pattern to search for (supports regex)
            new_value: Text to replace matches with
            
        Returns:
            List of results indicating replacements made in each file
        """
        replace_request = ReplaceRequest(
            files=files, new_value=new_value, pattern=pattern
        )

        return self.toolbox_api.replace_in_files(
            workspace_id=self.instance.id, replace_request=replace_request
        )

    @intercept_exceptions(message_prefix="Failed to search files: ")
    def search_files(self, path: str, pattern: str) -> SearchFilesResponse:
        """Searches for files matching a pattern in their names.
        
        Args:
            path: Root directory to start search from
            pattern: Pattern to match against file names
            
        Returns:
            Search results containing matching file paths
        """
        return self.toolbox_api.search_files(
            workspace_id=self.instance.id, path=path, pattern=pattern
        )

    @intercept_exceptions(message_prefix="Failed to set file permissions: ")
    def set_file_permissions(
        self, path: str, mode: str = None, owner: str = None, group: str = None
    ) -> None:
        """Sets permissions and ownership for a file or directory.
        
        Args:
            path: Path to the file/directory
            mode: File mode/permissions in octal format (e.g. "644") (optional)
            owner: User owner of the file (optional)
            group: Group owner of the file (optional)
        """
        self.toolbox_api.set_file_permissions(
            workspace_id=self.instance.id,
            path=path,
            mode=mode,
            owner=owner,
            group=group,
        )

    @intercept_exceptions(message_prefix="Failed to upload file: ")
    def upload_file(self, path: str, file: bytes) -> None:
        """Uploads a file to the workspace.
        
        Args:
            path: Destination path in the workspace
            file: File contents as bytes
        """
        self.toolbox_api.upload_file(
            workspace_id=self.instance.id, path=path, file=file
        )
