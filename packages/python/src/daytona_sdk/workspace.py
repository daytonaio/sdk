"""
Core workspace functionality for Daytona.

This module provides the main Workspace class that coordinates file system,
Git, process execution, and LSP functionality.
"""

import json
import time
from typing import Dict, Optional
from daytona_sdk._utils.exceptions import intercept_exceptions
from .filesystem import FileSystem
from .git import Git
from .process import Process
from .lsp_server import LspServer, LspLanguageId
from daytona_api_client import Workspace as ApiWorkspace, ToolboxApi, WorkspaceApi, WorkspaceInfo as ApiWorkspaceInfo
from .protocols import WorkspaceCodeToolbox
from dataclasses import dataclass
from datetime import datetime
from daytona_sdk._utils.exceptions import DaytonaException
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
    """Resources allocated to a workspace."""
    cpu: str
    gpu: Optional[str]
    memory: str
    disk: str


@dataclass
class WorkspaceState(Enum):
    """States of a workspace."""
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
    """Structured information about a workspace."""
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
    provider_metadata: Annotated[Optional[str], Field(deprecated='The `provider_metadata` field is deprecated. Use `state`, `node_domain`, `region`, `class_name`, `updated_at`, `last_snapshot`, `resources`, `auto_stop_interval` instead.')]


class WorkspaceInstance(ApiWorkspace):
    """Represents a Daytona workspace instance."""
    info: Optional[WorkspaceInfo]



class Workspace:
    """Represents a Daytona workspace instance.

    A workspace provides file system operations, Git operations, process execution,
    and LSP functionality.

    Args:
        id: Unique identifier for the workspace
        instance: The underlying workspace instance
        workspace_api: API client for workspace operations
        toolbox_api: API client for workspace operations
        code_toolbox: Language-specific toolbox implementation

    Attributes:
        fs: File system operations interface for managing files and directories
        git: Git operations interface for version control functionality
        process: Process execution interface for running commands and code
    """

    def __init__(
        self,
        id: str,
        instance: WorkspaceInstance,
        workspace_api: WorkspaceApi,
        toolbox_api: ToolboxApi,
        code_toolbox: WorkspaceCodeToolbox,
    ):
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
        """Get structured information about the workspace.

        Returns:
            WorkspaceInfo: Structured workspace information
        """
        instance = self.workspace_api.get_workspace(self.id)
        return Workspace._to_workspace_info(instance)

    @intercept_exceptions(message_prefix="Failed to get workspace root directory: ")
    def get_workspace_root_dir(self) -> str:
        """Gets the root directory path of the workspace.

        Returns:
            The absolute path to the workspace root
        """
        response = self.toolbox_api.get_project_dir(
            workspace_id=self.instance.id
        )
        return response.dir

    def create_lsp_server(
        self, language_id: LspLanguageId, path_to_project: str
    ) -> LspServer:
        """Creates a new Language Server Protocol (LSP) server instance.

        Args:
            language_id: The language server type
            path_to_project: Path to the project root

        Returns:
            A new LSP server instance
        """
        return LspServer(language_id, path_to_project, self.toolbox_api, self.instance)

    @intercept_exceptions(message_prefix="Failed to set labels: ")
    def set_labels(self, labels: Dict[str, str]) -> Dict[str, str]:
        """Sets labels for the workspace.

        Args:
            labels: Dictionary of key-value pairs representing workspace labels

        Returns:
            Dictionary containing the updated workspace labels

        Raises:
            DaytonaException: If the server request fails; If there's a network/connection error
        """
        # Convert all values to strings and create the expected labels structure
        string_labels = {k: str(v).lower() if isinstance(
            v, bool) else str(v) for k, v in labels.items()}
        labels_payload = {"labels": string_labels}
        return self.workspace_api.replace_labels(self.id, labels_payload)

    @intercept_exceptions(message_prefix="Failed to start workspace: ")
    @with_timeout(error_message=lambda self, timeout: f"Workspace {self.id} failed to start within the {timeout} seconds timeout period")
    def start(self, timeout: Optional[float] = 60):
        """Starts the workspace.

        Args:
            timeout: Maximum time to wait in seconds. 0 means no timeout. Default is 60 seconds.

        Raises:
            DaytonaException: If timeout is negative; If workspace fails to start or times out
        """
        self.workspace_api.start_workspace(self.id, _request_timeout=timeout)
        self.wait_for_workspace_start()

    @intercept_exceptions(message_prefix="Failed to stop workspace: ")
    @with_timeout(error_message=lambda self, timeout: f"Workspace {self.id} failed to stop within the {timeout} seconds timeout period")
    def stop(self, timeout: Optional[float] = 60):
        """Stops the workspace.

        Args:
            timeout: Maximum time to wait in seconds. 0 means no timeout. Default is 60 seconds.

        Raises:
            DaytonaException: If timeout is negative; If workspace fails to stop or times out
        """
        self.workspace_api.stop_workspace(self.id, _request_timeout=timeout)
        self.wait_for_workspace_stop()

    @intercept_exceptions(message_prefix="Failure during waiting for workspace to start: ")
    @with_timeout(error_message=lambda self, timeout: f"Workspace {self.id} failed to become ready within the {timeout} seconds timeout period")
    def wait_for_workspace_start(self, timeout: Optional[float] = 60) -> None:
        """Wait for workspace to reach 'started' state.

        Args:
            timeout: Maximum time to wait in seconds. 0 means no timeout. Default is 60 seconds.

        Raises:
            DaytonaException: If timeout is negative; If workspace fails to start or times out
        """
        state = None
        while state != "started":
            response = self.workspace_api.get_workspace(self.id)
            provider_metadata = json.loads(response.info.provider_metadata)
            state = provider_metadata.get('state', '')

            if state == "error":
                raise DaytonaException(
                    f"Workspace {self.id} failed to start with state: {state}")

            time.sleep(0.1)  # Wait 100ms between checks

    @intercept_exceptions(message_prefix="Failure during waiting for workspace to stop: ")
    @with_timeout(error_message=lambda self, timeout: f"Workspace {self.id} failed to become stopped within the {timeout} seconds timeout period")
    def wait_for_workspace_stop(self, timeout: Optional[float] = 60) -> None:
        """Wait for workspace to reach 'stopped' state.

        Args:
            timeout: Maximum time to wait in seconds. 0 means no timeout. Default is 60 seconds.

        Raises:
            DaytonaException: If timeout is negative; If workspace fails to stop or times out
        """
        state = None
        while state != "stopped":
            try:
                workspace_check = self.workspace_api.get_workspace(self.id)
                provider_metadata = json.loads(
                    workspace_check.info.provider_metadata)
                state = provider_metadata.get('state')

                if state == "error":
                    raise DaytonaException(
                        f"Workspace {self.id} failed to stop with status: {state}")
            except Exception as e:
                # If there's a validation error, continue waiting
                if "validation error" not in str(e):
                    raise e

            time.sleep(0.1)  # Wait 100ms between checks

    @intercept_exceptions(message_prefix="Failed to set auto-stop interval: ")
    def set_autostop_interval(self, interval: int) -> None:
        """Sets the auto-stop interval for the workspace.

        Args:
            interval: Number of minutes after which the workspace will automatically stop.
                    Set to 0 to disable auto-stop.

        Raises:
            DaytonaException: If interval is negative
        """
        if not isinstance(interval, int) or interval < 0:
            raise DaytonaException("Auto-stop interval must be a non-negative integer")

        self.workspace_api.set_autostop_interval(self.id, interval)
        self.instance.auto_stop_interval = interval

    @intercept_exceptions(message_prefix="Failed to get preview link: ")
    def get_preview_link(self, port: int) -> str:
        """Gets the preview link for the workspace at a specific port. If the port is not open, it will open it and return the link.
        
        Args:
            port: The port to open the preview link on
            
        Returns:
            The preview link for the workspace at the specified port
        """
        provider_metadata = json.loads(self.instance.info.provider_metadata)
        node_domain = provider_metadata.get('nodeDomain', '')
        if not node_domain:
            raise DaytonaException("Node domain not found in provider metadata. Please contact support.")
        
        return f"https://{port}-{self.id}.{node_domain}"
    
    @staticmethod
    def _to_workspace_info(instance: ApiWorkspace) -> WorkspaceInfo:
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

        enum_state = to_enum(WorkspaceState, provider_metadata.get('state', ''))
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
            error_reason=provider_metadata.get('errorReason'),
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
