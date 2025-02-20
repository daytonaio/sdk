"""
The Daytona SDK core Sandbox functionality.

Provides the main Workspace class representing a Daytona Sandbox that coordinates file system,
Git, process execution, and LSP functionality. It serves as the central point
for interacting with Daytona Sandboxes.

Example:
    Basic Sandbox operations:
    ```python
    from daytona_sdk import Daytona
    daytona = Daytona()
    workspace = daytona.create()
    
    # File operations
    workspace.fs.upload_file("/workspace/test.txt", b"Hello, World!")
    content = workspace.fs.download_file("/workspace/test.txt")
    
    # Git operations
    workspace.git.clone("https://github.com/user/repo.git")
    
    # Process execution
    response = workspace.process.exec("ls -la")
    print(response.result)
    
    # LSP functionality
    lsp = workspace.create_lsp_server("python", "/workspace/project")
    lsp.did_open("/workspace/project/src/index.ts")
    completions = lsp.completions("/workspace/project/src/index.ts", Position(line=10, character=15))
    print(completions)
    ```

Note:
    The Sandbox must be in a 'started' state before performing operations.
"""

import json
import time
from typing import Dict, Optional
from .filesystem import FileSystem
from .git import Git
from .process import Process
from .lsp_server import LspServer, LspLanguageId
from daytona_api_client import Workspace as WorkspaceInstance, ToolboxApi, WorkspaceApi
from .protocols import WorkspaceCodeToolbox
from dataclasses import dataclass
from datetime import datetime


@dataclass
class WorkspaceResources:
    """Resources allocated to a Sandbox.

    Attributes:
        cpu (str): Number of CPU cores allocated (e.g., "1", "2").
        gpu (Optional[str]): Number of GPUs allocated (e.g., "1") or None if no GPU.
        memory (str): Amount of memory allocated with unit (e.g., "2Gi", "4Gi").
        disk (str): Amount of disk space allocated with unit (e.g., "10Gi", "20Gi").

    Example:
        ```python
        resources = WorkspaceResources(
            cpu="2",
            gpu="1",
            memory="4Gi",
            disk="20Gi"
        )
        ```
    """
    cpu: str
    gpu: Optional[str]
    memory: str
    disk: str


@dataclass
class WorkspaceInfo:
    """Structured information about a Sandbox.

    This class provides detailed information about a Sandbox's configuration,
    resources, and current state.

    Attributes:
        id (str): Unique identifier for the Sandbox.
        name (str): Display name of the Sandbox.
        image (str): Docker image used for the Sandbox.
        user (str): OS user running in the Sandbox.
        env (Dict[str, str]): Environment variables set in the Sandbox.
        labels (Dict[str, str]): Custom labels attached to the Sandbox.
        public (bool): Whether the Sandbox is publicly accessible.
        target (str): Target environment where the Sandbox runs.
        resources (WorkspaceResources): Resource allocations for the Sandbox.
        state (str): Current state of the Sandbox (e.g., "started", "stopped").
        error_reason (Optional[str]): Error message if Sandbox is in error state.
        snapshot_state (Optional[str]): Current state of Sandbox snapshot.
        snapshot_state_created_at (Optional[datetime]): When the snapshot state was created.

    Example:
        ```python
        workspace = daytona.create()
        info = workspace.info()
        print(f"Workspace {info.name} is {info.state}")
        print(f"Resources: {info.resources.cpu} CPU, {info.resources.memory} RAM")
        ```
    """
    id: str
    name: str
    image: str
    user: str
    env: Dict[str, str]
    labels: Dict[str, str]
    public: bool
    target: str
    resources: WorkspaceResources
    state: str
    error_reason: Optional[str]
    snapshot_state: Optional[str]
    snapshot_state_created_at: Optional[datetime]


class Workspace:
    """Represents a Daytona Sandbox.

    A Sandbox provides file system operations, Git operations, process execution,
    and LSP functionality. It serves as the main interface for interacting with
    a Daytona Sandbox.

    Attributes:
        id (str): Unique identifier for the Sandbox.
        instance (WorkspaceInstance): The underlying Sandbox instance.
        workspace_api (WorkspaceApi): API client for Sandbox operations.
        toolbox_api (ToolboxApi): API client for toolbox operations.
        code_toolbox (WorkspaceCodeToolbox): Language-specific toolbox implementation.
        fs (FileSystem): File system operations interface.
        git (Git): Git operations interface.
        process (Process): Process execution interface.
    """

    def __init__(
        self,
        id: str,
        instance: WorkspaceInstance,
        workspace_api: WorkspaceApi,
        toolbox_api: ToolboxApi,
        code_toolbox: WorkspaceCodeToolbox,
    ):
        """Initialize a new Workspace instance.

        Args:
            id (str): Unique identifier for the Sandbox.
            instance (WorkspaceInstance): The underlying Sandbox instance.
            workspace_api (WorkspaceApi): API client for Sandbox operations.
            toolbox_api (ToolboxApi): API client for toolbox operations.
            code_toolbox (WorkspaceCodeToolbox): Language-specific toolbox implementation.
        """
        self.id = id
        self.instance = instance
        self.workspace_api = workspace_api
        self.toolbox_api = toolbox_api
        self.code_toolbox = code_toolbox

        # Initialize components
        # File system operations
        self.fs = FileSystem(instance, self.toolbox_api)
        self.git = Git(self, self.toolbox_api, instance)  # Git operations
        self.process = Process(
            self.code_toolbox, self.toolbox_api, instance)  # Process execution

    def info(self) -> WorkspaceInfo:
        """Gets structured information about the Sandbox.

        Returns:
            WorkspaceInfo: Detailed information about the Sandbox including its
                configuration, resources, and current state.

        Example:
            ```python
            info = workspace.info()
            print(f"Workspace {info.name}:")
            print(f"State: {info.state}")
            print(f"Resources: {info.resources.cpu} CPU, {info.resources.memory} RAM")
            ```
        """
        instance = self.instance
        provider_metadata = json.loads(instance.info.provider_metadata)

        # Extract resources from the correct location in provider_metadata
        # Resources might be directly in provider_metadata or in a nested structure
        resources_data = provider_metadata.get('resources', {})
        if isinstance(resources_data, dict):
            resources = WorkspaceResources(
                # Default to '1' if not specified
                cpu=str(resources_data.get('cpu', '1')),
                gpu=str(resources_data.get('gpu')
                        ) if resources_data.get('gpu') else None,
                # Default to '2Gi' if not specified
                memory=str(resources_data.get('memory', '2Gi')),
                # Default to '10Gi' if not specified
                disk=str(resources_data.get('disk', '10Gi'))
            )
        else:
            # Fallback to default values if resources structure is unexpected
            resources = WorkspaceResources(
                cpu='1',
                gpu=None,
                memory='2Gi',
                disk='10Gi'
            )

        return WorkspaceInfo(
            id=instance.id,
            name=instance.name,
            image=instance.image,
            user=instance.user,
            env=instance.env or {},
            labels=instance.labels or {},
            public=instance.public,
            target=instance.target,
            resources=resources,
            state=provider_metadata.get('state', ''),
            error_reason=provider_metadata.get('error_reason'),
            snapshot_state=provider_metadata.get('snapshot_state'),
            snapshot_state_created_at=datetime.fromisoformat(provider_metadata.get(
                'snapshot_state_created_at')) if provider_metadata.get('snapshot_state_created_at') else None
        )

    def get_workspace_root_dir(self) -> str:
        """Gets the root directory path of the Sandbox.

        Returns:
            str: The absolute path to the Sandbox root directory.

        Example:
            ```python
            root_dir = workspace.get_workspace_root_dir()
            print(f"Workspace root: {root_dir}")
            ```
        """
        response = self.toolbox_api.get_project_dir(
            workspace_id=self.instance.id
        )
        return response.dir

    def create_lsp_server(
        self, language_id: LspLanguageId, path_to_project: str
    ) -> LspServer:
        """Creates a new Language Server Protocol (LSP) server instance.

        The LSP server provides language-specific features like code completion,
        diagnostics, and more.

        Args:
            language_id (LspLanguageId): The language server type (e.g., "python", "typescript").
            path_to_project (str): Absolute path to the project root directory.

        Returns:
            LspServer: A new LSP server instance configured for the specified language.

        Example:
            ```python
            lsp = workspace.create_lsp_server("python", "/workspace/project")
            ```
        """
        return LspServer(language_id, path_to_project, self.toolbox_api, self.instance)

    def set_labels(self, labels: Dict[str, str]) -> Dict[str, str]:
        """Sets labels for the Sandbox.

        Labels are key-value pairs that can be used to organize and identify Sandboxes.

        Args:
            labels (Dict[str, str]): Dictionary of key-value pairs representing Sandbox labels.

        Returns:
            Dict[str, str]: Dictionary containing the updated Sandbox labels.

        Example:
            ```python
            new_labels = workspace.set_labels({
                "project": "my-project",
                "environment": "development",
                "team": "backend"
            })
            print(f"Updated labels: {new_labels}")
            ```
        """
        # Convert all values to strings and create the expected labels structure
        string_labels = {k: str(v).lower() if isinstance(
            v, bool) else str(v) for k, v in labels.items()}
        labels_payload = {"labels": string_labels}
        return self.workspace_api.replace_labels(self.id, labels_payload)

    def start(self, timeout: Optional[float] = None):
        """Starts the Sandbox.

        This method starts the Sandbox and waits for it to be ready.

        Args:
            timeout (Optional[float]): Maximum time to wait in seconds. 0 means no timeout.
                Defaults to 60-second timeout.

        Raises:
            ValueError: If timeout is negative.
            Exception: If Sandbox fails to start or times out.

        Example:
            ```python
            workspace = daytona.get_current_workspace("my-workspace")
            workspace.start(timeout=40)  # Wait up to 40 seconds
            print("Workspace started successfully")
            ```
        """
        self.workspace_api.start_workspace(self.id)
        self.wait_for_workspace_start(timeout)

    def stop(self):
        """Stops the Sandbox.

        This method stops the Sandbox and waits for it to be fully stopped.

        Example:
            ```python
            workspace = daytona.get_current_workspace("my-workspace")
            workspace.stop()
            print("Workspace stopped successfully")
            ```
        """
        self.workspace_api.stop_workspace(self.id)
        self.wait_for_workspace_stop()

    def wait_for_workspace_start(self, timeout: float = 60) -> None:
        """Waits for the Sandbox to reach the 'started' state.

        This method polls the Sandbox status until it reaches the 'started' state
        or encounters an error.

        Args:
            timeout (float): Maximum time to wait in seconds. 0 means no timeout.
                Defaults to 60 seconds.

        Raises:
            ValueError: If timeout is negative.
            Exception: If Sandbox fails to start or times out.
        """
        timeout = 60 if timeout is None else timeout
        if timeout < 0:
            raise ValueError("Timeout must be a non-negative number")

        check_interval = 0.1  # Wait 100ms between checks
        start_time = time.time()

        while timeout == 0 or (time.time() - start_time) < timeout:
            response = self.workspace_api.get_workspace(self.id)
            provider_metadata = json.loads(response.info.provider_metadata)
            state = provider_metadata.get('state', '')

            if state == "started":
                return

            if state == "error":
                raise Exception(
                    f"Workspace {self.id} failed to start with state: {state}")

            time.sleep(check_interval)

        raise Exception(
            "Workspace {self.id} failed to become ready within the timeout period")

    def wait_for_workspace_stop(self) -> None:
        """Waits for the Sandbox to reach the 'stopped' state.

        This method polls the Sandbox status until it reaches the 'stopped' state
        or encounters an error. It will wait up to 60 seconds for the Sandbox to stop.

        Raises:
            Exception: If Sandbox fails to stop or times out.
        """
        max_attempts = 600
        attempts = 0

        while attempts < max_attempts:
            try:
                workspace_check = self.workspace_api.get_workspace(self.id)
                provider_metadata = json.loads(
                    workspace_check.info.provider_metadata)
                state = provider_metadata.get('state')

                if state == "stopped":
                    return

                if state == "error":
                    raise Exception(
                        f"Workspace {self.id} failed to stop with status: {state}")
            except Exception as e:
                print(f"Exception: {e}")
                # If there's a validation error, continue waiting
                if "validation error" not in str(e):
                    raise e

            time.sleep(0.1)
            attempts += 1

        raise Exception(
            "Workspace {self.id} failed to become stopped within the timeout period")

    def set_autostop_interval(self, interval: int) -> None:
        """Sets the auto-stop interval for the Sandbox.

        The Sandbox will automatically stop after being idle (no new events) for the specified interval.
        Events include any state changes or interactions with the Sandbox through the SDK.
        Interactions using Sandbox Previews are not included.

        Args:
            interval (int): Number of minutes of inactivity before auto-stopping.
                Set to 0 to disable auto-stop. Defaults to 15.

        Example:
            ```python
            # Auto-stop after 1 hour
            workspace.set_autostop_interval(60)
            # Or disable auto-stop
            workspace.set_autostop_interval(0)
            ```
        """
        if not isinstance(interval, int) or interval < 0:
            raise ValueError(
                "Auto-stop interval must be a non-negative integer")

        self.workspace_api.set_autostop_interval(self.id, interval)
        self.instance.auto_stop_interval = interval
