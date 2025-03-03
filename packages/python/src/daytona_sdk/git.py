"""
The Daytona SDK provides built-in Git support. This guide covers all available Git
operations and best practices. Daytona SDK provides an option to clone, check status,
and manage Git repositories in Sandboxes. You can interact with Git repositories using
the `git` module.

Example:
    Basic Git workflow:
    ```python
    workspace = daytona.create()
    
    # Clone a repository
    workspace.git.clone(
        url="https://github.com/user/repo.git",
        path="/workspace/repo"
    )
    
    # Make some changes
    workspace.fs.upload_file("/workspace/repo/test.txt", "Hello, World!")
    
    # Stage and commit changes
    workspace.git.add("/workspace/repo", ["test.txt"])
    workspace.git.commit(
        path="/workspace/repo",
        message="Add test file",
        author="John Doe",
        email="john@example.com"
    )
    
    # Push changes (with authentication)
    workspace.git.push(
        path="/workspace/repo",
        username="user",
        password="token"
    )
    ```

Note:
    All paths should be absolute paths within the Sandbox if not explicitly
    stated otherwise.
"""

from typing import List, Optional, TYPE_CHECKING
from daytona_api_client import (
    GitStatus,
    ListBranchResponse,
    ToolboxApi,
    GitAddRequest,
    GitCloneRequest,
    GitCommitRequest,
    GitRepoRequest,
)
from daytona_sdk._utils.errors import intercept_errors
from .protocols import WorkspaceInstance

if TYPE_CHECKING:
    from .workspace import Workspace


class Git:
    """Provides Git operations within a Sandbox.

    This class implements a high-level interface to Git operations that can be
    performed within a Daytona Sandbox. It supports common Git operations like
    cloning repositories, staging and committing changes, pushing and pulling
    changes, and checking repository status.

    Attributes:
        workspace (Workspace): The parent Sandbox instance.
        instance (WorkspaceInstance): The Sandbox instance this Git handler belongs to.

    Example:
        ```python
        # Clone a repository
        workspace.git.clone(
            url="https://github.com/user/repo.git",
            path="/workspace/repo"
        )

        # Check repository status
        status = workspace.git.status("/workspace/repo")
        print(f"Modified files: {status.modified}")

        # Stage and commit changes
        workspace.git.add("/workspace/repo", ["file.txt"])
        workspace.git.commit(
            path="/workspace/repo",
            message="Update file",
            author="John Doe",
            email="john@example.com"
        )
        ```
    """

    def __init__(
        self,
        workspace: "Workspace",
        toolbox_api: ToolboxApi,
        instance: WorkspaceInstance,
    ):
        """Initializes a new Git handler instance.

        Args:
            workspace (Workspace): The parent Sandbox instance.
            toolbox_api (ToolboxApi): API client for Sandbox operations.
            instance (WorkspaceInstance): The Sandbox instance this Git handler belongs to.
        """
        self.workspace = workspace
        self.toolbox_api = toolbox_api
        self.instance = instance

    @intercept_errors(message_prefix="Failed to add files: ")
    def add(self, path: str, files: List[str]) -> None:
        """Stages files for commit.

        This method stages the specified files for the next commit, similar to
        running 'git add' on the command line.

        Args:
            path (str): Absolute path to the Git repository root.
            files (List[str]): List of file paths or directories to stage, relative to the repository root.

        Example:
            ```python
            # Stage a single file
            workspace.git.add("/workspace/repo", ["file.txt"])

            # Stage multiple files
            workspace.git.add("/workspace/repo", [
                "src/main.py",
                "tests/test_main.py",
                "README.md"
            ])
            ```
        """
        self.toolbox_api.git_add_files(
            workspace_id=self.instance.id,
            git_add_request=GitAddRequest(
                path=path,
                files=files
            ),
        )

    @intercept_errors(message_prefix="Failed to list branches: ")
    def branches(self, path: str) -> ListBranchResponse:
        """Lists branches in the repository.

        This method returns information about all branches in the repository.

        Args:
            path (str): Absolute path to the Git repository root.

        Returns:
            ListBranchResponse: List of branches in the repository.

        Example:
            ```python
            response = workspace.git.branches("/workspace/repo")
            print(f"Branches: {response.branches}")
            ```
        """
        return self.toolbox_api.git_list_branches(
            workspace_id=self.instance.id,
            path=path,
        )

    @intercept_errors(message_prefix="Failed to clone repository: ")
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

        This method clones a Git repository into the specified path. It supports
        cloning specific branches or commits, and can authenticate with the remote
        repository if credentials are provided.

        Args:
            url (str): Repository URL to clone from.
            path (str): Absolute path where the repository should be cloned.
            branch (Optional[str]): Specific branch to clone. If not specified,
                clones the default branch.
            commit_id (Optional[str]): Specific commit to clone. If specified,
                the repository will be left in a detached HEAD state at this commit.
            username (Optional[str]): Git username for authentication.
            password (Optional[str]): Git password or token for authentication.

        Example:
            ```python
            # Clone the default branch
            workspace.git.clone(
                url="https://github.com/user/repo.git",
                path="/workspace/repo"
            )

            # Clone a specific branch with authentication
            workspace.git.clone(
                url="https://github.com/user/private-repo.git",
                path="/workspace/private",
                branch="develop",
                username="user",
                password="token"
            )

            # Clone a specific commit
            workspace.git.clone(
                url="https://github.com/user/repo.git",
                path="/workspace/repo-old",
                commit_id="abc123"
            )
            ```
        """
        self.toolbox_api.git_clone_repository(
            workspace_id=self.instance.id,
            git_clone_request=GitCloneRequest(
                url=url,
                branch=branch,
                path=path,
                username=username,
                password=password,
                commitId=commit_id,
            )
        )

    @intercept_errors(message_prefix="Failed to commit changes: ")
    def commit(self, path: str, message: str, author: str, email: str) -> None:
        """Commits staged changes.

        This method creates a new commit with the staged changes. Make sure to stage
        changes using the add() method before committing.

        Args:
            path (str): Absolute path to the Git repository root.
            message (str): Commit message describing the changes.
            author (str): Name of the commit author.
            email (str): Email address of the commit author.

        Example:
            ```python
            # Stage and commit changes
            workspace.git.add("/workspace/repo", ["README.md"])
            workspace.git.commit(
                path="/workspace/repo",
                message="Update documentation",
                author="John Doe",
                email="john@example.com"
            )
            ```
        """
        self.toolbox_api.git_commit_changes(
            workspace_id=self.instance.id,
            git_commit_request=GitCommitRequest(
                path=path,
                message=message,
                author=author,
                email=email
            ),
        )

    @intercept_errors(message_prefix="Failed to push changes: ")
    def push(
        self, path: str, username: Optional[str] = None, password: Optional[str] = None
    ) -> None:
        """Pushes local commits to the remote repository.

        This method pushes all local commits on the current branch to the remote
        repository. If the remote repository requires authentication, provide
        username and password/token.

        Args:
            path (str): Absolute path to the Git repository root.
            username (Optional[str]): Git username for authentication.
            password (Optional[str]): Git password or token for authentication.

        Example:
            ```python
            # Push without authentication (for public repos or SSH)
            workspace.git.push("/workspace/repo")

            # Push with authentication
            workspace.git.push(
                path="/workspace/repo",
                username="user",
                password="github_token"
            )
            ```
        """
        self.toolbox_api.git_push_changes(
            workspace_id=self.instance.id,
            git_repo_request=GitRepoRequest(
                path=path,
                username=username,
                password=password
            ),
        )

    @intercept_errors(message_prefix="Failed to pull changes: ")
    def pull(
        self, path: str, username: Optional[str] = None, password: Optional[str] = None
    ) -> None:
        """Pulls changes from the remote repository.

        This method fetches and merges changes from the remote repository into
        the current branch. If the remote repository requires authentication,
        provide username and password/token.

        Args:
            path (str): Absolute path to the Git repository root.
            username (Optional[str]): Git username for authentication.
            password (Optional[str]): Git password or token for authentication.

        Example:
            ```python
            # Pull without authentication
            workspace.git.pull("/workspace/repo")

            # Pull with authentication
            workspace.git.pull(
                path="/workspace/repo",
                username="user",
                password="github_token"
            )
            ```
        """
        self.toolbox_api.git_pull_changes(
            workspace_id=self.instance.id,
            git_repo_request=GitRepoRequest(
                path=path,
                username=username,
                password=password
            ),
        )

    @intercept_errors(message_prefix="Failed to get status: ")
    def status(self, path: str) -> GitStatus:
        """Gets the current Git repository status.

        This method returns detailed information about the current state of the
        repository, including staged, unstaged, and untracked files.

        Args:
            path (str): Absolute path to the Git repository root.

        Returns:
            GitStatus: Repository status information including:
                - current_branch: Current branch name
                - file_status: List of file statuses
                - ahead: Number of local commits not pushed to remote
                - behind: Number of remote commits not pulled locally
                - branch_published: Whether the branch has been published to the remote repository

        Example:
            ```python
            status = workspace.git.status("/workspace/repo")
            print(f"On branch: {status.current_branch}")
            print(f"Commits ahead: {status.ahead}")
            print(f"Commits behind: {status.behind}")
            ```
        """
        return self.toolbox_api.git_get_status(
            workspace_id=self.instance.id,
            path=path,
        )
