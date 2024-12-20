"""
Git operations within a Daytona workspace.

This module provides functionality for managing Git repositories, including cloning,
committing changes, pushing/pulling, and checking repository status.
"""

from typing import List, Optional, TYPE_CHECKING
from api_client import (
    GitStatus,
    ListBranchResponse,
    Match,
    Workspace as WorkspaceInstance,
    WorkspaceToolboxApi,
)

if TYPE_CHECKING:
    from .workspace import Workspace


class Git:
    """Provides Git operations within a workspace.
    
    Args:
        workspace: The parent workspace instance
        toolbox_api: API client for workspace operations
        instance: The workspace instance
    """

    def __init__(
        self,
        workspace: "Workspace",
        toolbox_api: WorkspaceToolboxApi,
        instance: WorkspaceInstance,
    ):
        self.workspace = workspace
        self.toolbox_api = toolbox_api
        self.instance = instance

    def add(self, path: str, files: List[str]) -> None:
        """Stages files for commit.
        
        Args:
            path: Repository path
            files: List of file paths to stage
        """
        self.toolbox_api.git_add_files(
            workspace_id=self.instance.id,
            project_id="main",
            params={"path": path, "files": files},
        )

    def branches(self, path: str) -> ListBranchResponse:
        """Lists branches in the repository.
        
        Args:
            path: Repository path
        
        Returns:
            List of branches and their information
        """
        return self.toolbox_api.git_branch_list(
            workspace_id=self.instance.id,
            project_id="main",
            path=path,
        )

    def clone(
        self,
        url: str,
        path: str,
        branch: Optional[str] = None,
        commit_id: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """Clones a Git repository.
        
        Args:
            url: Repository URL
            path: Destination path
            branch: Branch to clone (optional)
            commit_id: Specific commit to clone (optional)
            username: Git username for authentication (optional)
            password: Git password/token for authentication (optional)
        """
        self.toolbox_api.git_clone_repository(
            workspace_id=self.instance.id,
            project_id="main",
            params={
                "url": url,
                "branch": branch,
                "path": path,
                "username": username,
                "password": password,
                "commitId": commit_id,
            },
        )

    def commit(self, path: str, message: str, author: str, email: str) -> None:
        """Commits staged changes.
        
        Args:
            path: Repository path
            message: Commit message
            author: Name of the commit author
            email: Email of the commit author
        """
        self.toolbox_api.git_commit_changes(
            workspace_id=self.instance.id,
            project_id="main",
            params={"path": path, "message": message, "author": author, "email": email},
        )

    def push(
        self, path: str, username: Optional[str] = None, password: Optional[str] = None
    ) -> None:
        """Pushes local commits to the remote repository.
        
        Args:
            path: Repository path
            username: Git username for authentication (optional)
            password: Git password/token for authentication (optional)
        """
        self.toolbox_api.git_push_changes(
            workspace_id=self.instance.id,
            project_id="main",
            params={"path": path, "username": username, "password": password},
        )

    def pull(
        self, path: str, username: Optional[str] = None, password: Optional[str] = None
    ) -> None:
        """Pulls changes from the remote repository.
        
        Args:
            path: Repository path
            username: Git username for authentication (optional)
            password: Git password/token for authentication (optional)
        """
        self.toolbox_api.git_pull_changes(
            workspace_id=self.instance.id,
            project_id="main",
            params={"path": path, "username": username, "password": password},
        )

    def status(self, path: str) -> GitStatus:
        """Gets the current Git repository status.
        
        Args:
            path: Repository path
        
        Returns:
            Repository status information including staged, unstaged, and untracked files
        """
        return self.toolbox_api.git_git_status(
            workspace_id=self.instance.id,
            project_id="main",
            path=path,
        )
