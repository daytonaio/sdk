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
from daytona_sdk._utils.errors import intercept_errors
from .filesystem import FileSystem
from .git import Git
from .process import Process
from .lsp_server import LspServer, LspLanguageId
from daytona_api_client import Workspace as ApiWorkspace, ToolboxApi, WorkspaceApi, WorkspaceInfo as ApiWorkspaceInfo
from .protocols import WorkspaceCodeToolbox
from dataclasses import dataclass
from datetime import datetime
from daytona_sdk._utils.errors import DaytonaError
from enum import Enum
from pydantic import Field
from typing_extensions import Annotated
from ._utils.enum import to_enum
from ._utils.timeout import with_timeout


@dataclass
class WorkspaceTargetRegion(Enum):
    """Target regions for workspaces"""
    EU = "eu"
    US = "us"
    ASIA = "asia"

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)


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
class WorkspaceState(Enum):
    """States of a Sandbox."""
    CREATING = "creating"
    RESTORING = "restoring"
    DESTROYED = "destroyed"
    DESTROYING = "destroying"
    STARTED = "started"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    RESIZING = "resizing"
    ERROR = "error"
    UNKNOWN = "unknown"
    PULLING_IMAGE = "pulling_image"

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)


class WorkspaceInfo(ApiWorkspaceInfo):
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
    target: WorkspaceTargetRegion
    resources: WorkspaceResources
    state: WorkspaceState
    error_reason: Optional[str]
    snapshot_state: Optional[str]
    snapshot_state_created_at: Optional[datetime]
    node_domain: str
    region: str
    class_name: str
    updated_at: str
    last_snapshot: Optional[str]
    auto_stop_interval: int
    provider_metadata: Annotated[Optional[str], Field(
        deprecated='The `provider_metadata` field is deprecated. Use `state`, `node_domain`, `region`, `class_name`, `updated_at`, `last_snapshot`, `resources`, `auto_stop_interval` instead.')]


class WorkspaceInstance(ApiWorkspace):
    """Represents a Daytona workspace instance."""
    info: Optional[WorkspaceInfo]


class Workspace:
    """Represents a Daytona Sandbox.

    A Sandbox provides file system operations, Git operations, process execution,
    and LSP functionality. It serves as the main interface for interacting with
    a Daytona Sandbox.

    Attributes:
        id (str): Unique identifier for the Sandbox.
        instance (WorkspaceInstance): The underlying Sandbox instance.
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
        instance = self.workspace_api.get_workspace(self.id)
        return Workspace._to_workspace_info(instance)

    @intercept_errors(message_prefix="Failed to get workspace root directory: ")
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
            language_id (LspLanguageId): The language server type (e.g., LspLanguageId.PYTHON).
            path_to_project (str): Absolute path to the project root directory.

        Returns:
            LspServer: A new LSP server instance configured for the specified language.

        Example:
            ```python
            lsp = workspace.create_lsp_server("python", "/workspace/project")
            ```
        """
        return LspServer(language_id, path_to_project, self.toolbox_api, self.instance)

    @intercept_errors(message_prefix="Failed to set labels: ")
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

    @intercept_errors(message_prefix="Failed to start workspace: ")
    @with_timeout(error_message=lambda self, timeout: f"Workspace {self.id} failed to start within the {timeout} seconds timeout period")
    def start(self, timeout: Optional[float] = 60):
        """Starts the Sandbox.

        This method starts the Sandbox and waits for it to be ready.

        Args:
            timeout (Optional[float]): Maximum time to wait in seconds. 0 means no timeout. Default is 60 seconds.

        Raises:
            DaytonaError: If timeout is negative. If workspace fails to start or times out.

        Example:
            ```python
            workspace = daytona.get_current_workspace("my-workspace")
            workspace.start(timeout=40)  # Wait up to 40 seconds
            print("Workspace started successfully")
            ```
        """
        self.workspace_api.start_workspace(self.id, _request_timeout=timeout or None)
        self.wait_for_workspace_start()

    @intercept_errors(message_prefix="Failed to stop workspace: ")
    @with_timeout(error_message=lambda self, timeout: f"Workspace {self.id} failed to stop within the {timeout} seconds timeout period")
    def stop(self, timeout: Optional[float] = 60):
        """Stops the Sandbox.

        This method stops the Sandbox and waits for it to be fully stopped.

        Args:
            timeout (Optional[float]): Maximum time to wait in seconds. 0 means no timeout. Default is 60 seconds.

        Raises:
            DaytonaError: If timeout is negative; If workspace fails to stop or times out

        Example:
            ```python
            workspace = daytona.get_current_workspace("my-workspace")
            workspace.stop()
            print("Workspace stopped successfully")
            ```
        """
        self.workspace_api.stop_workspace(self.id, _request_timeout=timeout or None)
        self.wait_for_workspace_stop()

    @intercept_errors(message_prefix="Failure during waiting for workspace to start: ")
    @with_timeout(error_message=lambda self, timeout: f"Workspace {self.id} failed to become ready within the {timeout} seconds timeout period")
    def wait_for_workspace_start(self, timeout: Optional[float] = 60) -> None:
        """Waits for the Sandbox to reach the 'started' state.

        This method polls the Sandbox status until it reaches the 'started' state
        or encounters an error.

        Args:
            timeout (Optional[float]): Maximum time to wait in seconds. 0 means no timeout. Default is 60 seconds.

        Raises:
            DaytonaError: If timeout is negative; If workspace fails to start or times out
        """
        state = None
        while state != "started":
            response = self.workspace_api.get_workspace(self.id)
            provider_metadata = json.loads(response.info.provider_metadata)
            state = provider_metadata.get('state', '')

            if state == "error":
                raise DaytonaError(
                    f"Workspace {self.id} failed to start with state: {state}, error reason: {response.error_reason}")

            time.sleep(0.1)  # Wait 100ms between checks

    @intercept_errors(message_prefix="Failure during waiting for workspace to stop: ")
    @with_timeout(error_message=lambda self, timeout: f"Workspace {self.id} failed to become stopped within the {timeout} seconds timeout period")
    def wait_for_workspace_stop(self, timeout: Optional[float] = 60) -> None:
        """Waits for the Sandbox to reach the 'stopped' state.

        This method polls the Sandbox status until it reaches the 'stopped' state
        or encounters an error. It will wait up to 60 seconds for the Sandbox to stop.

        Args:
            timeout (Optional[float]): Maximum time to wait in seconds. 0 means no timeout. Default is 60 seconds.

        Raises:
            DaytonaError: If timeout is negative. If Sandbox fails to stop or times out.
        """
        state = None
        while state != "stopped":
            try:
                workspace_check = self.workspace_api.get_workspace(self.id)
                provider_metadata = json.loads(
                    workspace_check.info.provider_metadata)
                state = provider_metadata.get('state')

                if state == "error":
                    raise DaytonaError(
                        f"Workspace {self.id} failed to stop with status: {state}, error reason: {workspace_check.error_reason}")
            except Exception as e:
                # If there's a validation error, continue waiting
                if "validation error" not in str(e):
                    raise e

            time.sleep(0.1)  # Wait 100ms between checks

    @intercept_errors(message_prefix="Failed to set auto-stop interval: ")
    def set_autostop_interval(self, interval: int) -> None:
        """Sets the auto-stop interval for the Sandbox.

        The Sandbox will automatically stop after being idle (no new events) for the specified interval.
        Events include any state changes or interactions with the Sandbox through the SDK.
        Interactions using Sandbox Previews are not included.

        Args:
            interval (int): Number of minutes of inactivity before auto-stopping.
                Set to 0 to disable auto-stop. Defaults to 15.

        Raises:
            DaytonaError: If interval is negative

        Example:
            ```python
            # Auto-stop after 1 hour
            workspace.set_autostop_interval(60)
            # Or disable auto-stop
            workspace.set_autostop_interval(0)
            ```
        """
        if not isinstance(interval, int) or interval < 0:
            raise DaytonaError(
                "Auto-stop interval must be a non-negative integer")

        self.workspace_api.set_autostop_interval(self.id, interval)
        self.instance.auto_stop_interval = interval

    @intercept_errors(message_prefix="Failed to get preview link: ")
    def get_preview_link(self, port: int) -> str:
        """Gets the preview link for the workspace at a specific port. If the port is not open, it will open it and return the link.

        Args:
            port (int): The port to open the preview link on

        Returns:
            The preview link for the workspace at the specified port
        """
        provider_metadata = json.loads(self.instance.info.provider_metadata)
        node_domain = provider_metadata.get('nodeDomain', '')
        if not node_domain:
            raise DaytonaError(
                "Node domain not found in provider metadata. Please contact support.")

        return f"https://{port}-{self.id}.{node_domain}"

    @intercept_errors(message_prefix="Failed to archive workspace: ")
    def archive(self) -> None:
        """Archives the workspace, making it inactive and preserving its state. When sandboxes are archived, the entire filesystem
        state is moved to cost-effective object storage, making it possible to keep sandboxes available for an extended period.
        The tradeoff between archived and stopped states is that starting an archived sandbox takes more time, depending on its size.
        Workspace must be stopped before archiving.
        """
        self.workspace_api.archive_workspace(self.id)

    @staticmethod
    def _to_workspace_info(instance: ApiWorkspace) -> WorkspaceInfo:
        """Converts an API workspace instance to a WorkspaceInfo object.

        Args:
            instance (ApiWorkspace): The API workspace instance to convert

        Returns:
            WorkspaceInfo: The converted WorkspaceInfo object
        """
        provider_metadata = json.loads(instance.info.provider_metadata or '{}')
        resources_data = provider_metadata.get('resources', provider_metadata)

        # Extract resources with defaults
        resources = WorkspaceResources(
            cpu=str(resources_data.get('cpu', '1')),
            gpu=str(resources_data.get('gpu')
                    ) if resources_data.get('gpu') else None,
            memory=str(resources_data.get('memory', '2')) + 'Gi',
            disk=str(resources_data.get('disk', '10')) + 'Gi'
        )

        enum_state = to_enum(
            WorkspaceState, provider_metadata.get('state', ''))
        enum_target = to_enum(WorkspaceTargetRegion, instance.target)

        return WorkspaceInfo(
            id=instance.id,
            name=instance.name,
            image=instance.image,
            user=instance.user,
            env=instance.env or {},
            labels=instance.labels or {},
            public=instance.public,
            target=enum_target or instance.target,
            resources=resources,
            state=enum_state or provider_metadata.get('state', ''),
            error_reason=instance.error_reason,
            snapshot_state=provider_metadata.get('snapshotState'),
            snapshot_state_created_at=datetime.fromisoformat(provider_metadata.get(
                'snapshotStateCreatedAt')) if provider_metadata.get('snapshotStateCreatedAt') else None,
            node_domain=provider_metadata.get('nodeDomain', ''),
            region=provider_metadata.get('region', ''),
            class_name=provider_metadata.get('class', ''),
            updated_at=provider_metadata.get('updatedAt', ''),
            last_snapshot=provider_metadata.get('lastSnapshot'),
            auto_stop_interval=provider_metadata.get('autoStopInterval', 0),
            created=instance.info.created or '',
            provider_metadata=instance.info.provider_metadata,
        )
