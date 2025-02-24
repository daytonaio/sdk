"""
Core workspace functionality for Daytona.

This module provides the main Workspace class that coordinates file system,
Git, process execution, and LSP functionality.
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
    """Resources allocated to a workspace."""
    cpu: str
    gpu: Optional[str]
    memory: str
    disk: str

@dataclass
class WorkspaceInfo:
    """Structured information about a workspace."""
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
        self.fs = FileSystem(instance, self.toolbox_api)  # File system operations
        self.git = Git(self, self.toolbox_api, instance)  # Git operations
        self.process = Process(self.code_toolbox, self.toolbox_api, instance)  # Process execution

    def info(self) -> WorkspaceInfo:
        """Get structured information about the workspace.
        
        Returns:
            WorkspaceInfo: Structured workspace information
        """
        instance = self.instance
        provider_metadata = json.loads(instance.info.provider_metadata)
        
        # Extract resources from the correct location in provider_metadata
        # Resources might be directly in provider_metadata or in a nested structure
        resources_data = provider_metadata.get('resources', {})
        if isinstance(resources_data, dict):
            resources = WorkspaceResources(
                cpu=str(resources_data.get('cpu', '1')),  # Default to '1' if not specified
                gpu=str(resources_data.get('gpu')) if resources_data.get('gpu') else None,
                memory=str(resources_data.get('memory', '2Gi')),  # Default to '2Gi' if not specified
                disk=str(resources_data.get('disk', '10Gi'))  # Default to '10Gi' if not specified
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
            snapshot_state_created_at=datetime.fromisoformat(provider_metadata.get('snapshot_state_created_at')) if provider_metadata.get('snapshot_state_created_at') else None
        )

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

    def set_labels(self, labels: Dict[str, str]) -> Dict[str, str]:
        """Sets labels for the workspace.
        
        Args:
            labels: Dictionary of key-value pairs representing workspace labels
            
        Returns:
            Dictionary containing the updated workspace labels
            
        Raises:
            urllib.error.HTTPError: If the server request fails
            urllib.error.URLError: If there's a network/connection error
        """
        # Convert all values to strings and create the expected labels structure
        string_labels = {k: str(v).lower() if isinstance(v, bool) else str(v) for k, v in labels.items()}
        labels_payload = {"labels": string_labels}
        return self.workspace_api.replace_labels(self.id, labels_payload)

    def start(self, timeout: Optional[float] = None):
        """Starts the workspace.

        Args:
            timeout: Maximum time to wait in seconds. 0 means no timeout.

        Raises:
            ValueError: If timeout is negative
            Exception: If workspace fails to start or times out
        """
        self.workspace_api.start_workspace(self.id)
        self.wait_for_workspace_start(timeout)


    def stop(self):
        """Stops the workspace."""
        self.workspace_api.stop_workspace(self.id)
        self.wait_for_workspace_stop()

    def wait_for_workspace_start(self, timeout: float = 60) -> None:
        """Wait for workspace to reach 'started' state.

        Args:
            timeout: Maximum time to wait in seconds. 0 means no timeout.

        Raises:
            ValueError: If timeout is negative
            Exception: If workspace fails to start or times out
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
        """Wait for workspace to reach 'stopped' state.
        
        Raises:
            Exception: If workspace fails to stop or times out
        """
        max_attempts = 600
        attempts = 0

        while attempts < max_attempts:
            try:
                workspace_check = self.workspace_api.get_workspace(self.id)
                provider_metadata = json.loads(workspace_check.info.provider_metadata)
                state = provider_metadata.get('state')

                if state == "stopped":
                    return
                    
                if state == "error":
                    raise Exception(f"Workspace {self.id} failed to stop with status: {state}")
            except Exception as e:
                print(f"Exception: {e}")
                # If there's a validation error, continue waiting
                if "validation error" not in str(e):
                    raise e
                
            time.sleep(0.1)
            attempts += 1
            
        raise Exception("Workspace {self.id} failed to become stopped within the timeout period")

    def set_autostop_interval(self, interval: int) -> None:
        """Sets the auto-stop interval for the workspace.

        Args:
            interval: Number of minutes after which the workspace will automatically stop.
                    Set to 0 to disable auto-stop.

        Raises:
            ValueError: If interval is negative
        """
        if not isinstance(interval, int) or interval < 0:
            raise ValueError("Auto-stop interval must be a non-negative integer")

        self.workspace_api.set_autostop_interval(self.id, interval)
        self.instance.auto_stop_interval = interval

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
            raise Exception("Cannot get preview link. Node domain not found in provider metadata. Please contact support.")
        
        return f"https://{port}-{self.id}.{node_domain}"
