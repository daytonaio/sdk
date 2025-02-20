"""
Provides the main entry point for interacting with Daytona Server API.

The Daytona allows you to create, manage, and interact with Daytona workspaces.
It provides a high-level interface for workspace operations including creation,
deletion, listing, and status management.

Example:
    Basic usage with environment variables:
    ```python
    from daytona_sdk import Daytona
    daytona = Daytona()  # Uses env vars DAYTONA_API_KEY, DAYTONA_SERVER_URL
    workspace = daytona.create()  # Creates a Python workspace
    # Run the code securely inside the workspace
    response = workspace.process.code_run('print("Hello World!")')
    print(response.result)
    daytona.remove(workspace)
    ```

    Usage with explicit configuration:
    ```python
    config = DaytonaConfig(
        api_key="your-api-key",
        server_url="https://your-server.com",
        target="us"
    )
    daytona = Daytona(config)
    ```
"""

import uuid
import json
from typing import Optional, Literal, Dict, Any, List
from dataclasses import dataclass
from environs import Env
import time
from daytona_api_client import (
    Configuration,
    WorkspaceApi,
    ToolboxApi,
    ApiClient,
    CreateWorkspace,
    SessionExecuteRequest,
    SessionExecuteResponse
)

from .code_toolbox.workspace_python_code_toolbox import WorkspacePythonCodeToolbox
from .code_toolbox.workspace_ts_code_toolbox import WorkspaceTsCodeToolbox
from .workspace import Workspace


# Type definitions
CodeLanguage = Literal["python", "javascript", "typescript"]


@dataclass
class DaytonaConfig:
    """Configuration options for initializing the Daytona client.

    Attributes:
        api_key (str): API key for authentication with Daytona server.
        server_url (str): URL of the Daytona server.
        target (str): Target environment for workspaces.

    Example:
        ```python
        config = DaytonaConfig(
            api_key="your-api-key",
            server_url="https://your-server.com",
            target="us"
        )
        daytona = Daytona(config)
        ```
    """
    api_key: str
    server_url: str
    target: str


@dataclass
class WorkspaceResources:
    """Resources configuration for workspace.

    Attributes:
        cpu (Optional[int]): Number of CPU cores to allocate.
        memory (Optional[int]): Amount of memory in GB to allocate.
        disk (Optional[int]): Amount of disk space in GB to allocate.
        gpu (Optional[int]): Number of GPUs to allocate.

    Example:
        ```python
        resources = WorkspaceResources(
            cpu=2,
            memory=4,  # 4GB RAM
            disk=20,   # 20GB disk
            gpu=1
        )
        params = CreateWorkspaceParams(
            language="python",
            resources=resources
        )
        ```
    """
    cpu: Optional[int] = None
    memory: Optional[int] = None
    disk: Optional[int] = None
    gpu: Optional[int] = None


@dataclass
class CreateWorkspaceParams:
    """Parameters for creating a new workspace.

    Attributes:
        language (CodeLanguage): Programming language for the workspace ("python", "javascript", "typescript").
        id (Optional[str]): Custom identifier for the workspace. If not provided, a random ID will be generated.
        name (Optional[str]): Display name for the workspace. Defaults to workspace ID if not provided.
        image (Optional[str]): Custom Docker image to use for the workspace.
        os_user (Optional[str]): OS user for the workspace. Defaults to "daytona".
        env_vars (Optional[Dict[str, str]]): Environment variables to set in the workspace.
        labels (Optional[Dict[str, str]]): Custom labels for the workspace.
        public (Optional[bool]): Whether the workspace should be public.
        target (Optional[str]): Target location for the workspace. Can be "us", "eu", or "asia".
        resources (Optional[WorkspaceResources]): Resource configuration for the workspace.
        timeout (Optional[float]): Timeout in seconds for workspace to be created and started.
        auto_stop_interval (Optional[int]): Interval in minutes after which workspace will automatically stop if no workspace event occurs during that time. Default is 15 minutes. If set to 0, the workspace will not be automatically stopped.

    Example:
        ```python
        params = CreateWorkspaceParams(
            language="python",
            name="my-workspace",
            env_vars={"DEBUG": "true"},
            resources=WorkspaceResources(cpu=2, memory=4),
            timeout=60,
            auto_stop_interval=20
        )
        workspace = daytona.create(params)
        ```
    """
    language: CodeLanguage
    id: Optional[str] = None
    name: Optional[str] = None
    image: Optional[str] = None
    os_user: Optional[str] = None
    env_vars: Optional[Dict[str, str]] = None
    labels: Optional[Dict[str, str]] = None
    public: Optional[bool] = None
    target: Optional[str] = None
    resources: Optional[WorkspaceResources] = None
    timeout: Optional[float] = None
    auto_stop_interval: Optional[int] = None


class Daytona:
    """Main class for interacting with Daytona Server API.

    This class provides methods to create, manage, and interact with Daytona workspaces.
    It can be initialized either with explicit configuration or using environment variables.

    Attributes:
        api_key (str): API key for authentication.
        server_url (str): URL of the Daytona server.
        target (str): Default target location for workspaces.
        workspace_api (WorkspaceApi): API client for workspace operations.
        toolbox_api (ToolboxApi): API client for toolbox operations.

    Example:
        Using environment variables:
        ```python
        daytona = Daytona()  # Uses DAYTONA_API_KEY, DAYTONA_SERVER_URL
        ```

        Using explicit configuration:
        ```python
        config = DaytonaConfig(
            api_key="your-api-key",
            server_url="https://your-server.com",
            target="us"
        )
        daytona = Daytona(config)
        ```
    """

    def __init__(self, config: Optional[DaytonaConfig] = None):
        """Initialize Daytona instance with optional configuration.

        If no config is provided, reads from environment variables:
        - `DAYTONA_API_KEY`: Required API key for authentication
        - `DAYTONA_SERVER_URL`: Required server URL
        - `DAYTONA_TARGET`: Optional target environment (defaults to "local")

        Args:
            config (Optional[DaytonaConfig]): Object containing api_key, server_url, and target.

        Raises:
            ValueError: If API key or Server URL is not provided either through config
                or environment variables.

        Example:
            ```python
            from daytona_sdk import Daytona, DaytonaConfig
            # Using environment variables
            daytona1 = Daytona()
            # Using explicit configuration
            config = DaytonaConfig(
                api_key="your-api-key",
                server_url="https://your-server.com",
                target="us"
            )
            daytona2 = Daytona(config)
            ```
        """
        if config is None:
            # Initialize env - it automatically reads from .env and .env.local
            env = Env()
            env.read_env()  # reads .env
            # reads .env.local and overrides values
            env.read_env(".env.local", override=True)

            self.api_key = env.str("DAYTONA_API_KEY")
            self.server_url = env.str("DAYTONA_SERVER_URL")
            self.target = env.str("DAYTONA_TARGET", "local")
        else:
            self.api_key = config.api_key
            self.server_url = config.server_url
            self.target = config.target

        if not self.api_key:
            raise ValueError("API key is required")

        if not self.server_url:
            raise ValueError("Server URL is required")

        # Create API configuration without api_key
        configuration = Configuration(host=self.server_url)
        api_client = ApiClient(configuration)
        api_client.default_headers["Authorization"] = f"Bearer {self.api_key}"

        # Initialize API clients with the api_client instance
        self.workspace_api = WorkspaceApi(api_client)
        self.toolbox_api = ToolboxApi(api_client)

    def create(self, params: Optional[CreateWorkspaceParams] = None) -> Workspace:
        """Creates a new workspace and waits for it to start.

        Args:
            params (Optional[CreateWorkspaceParams]): Parameters for workspace creation. If not provided,
                   defaults to Python language.

        Returns:
            Workspace: The created workspace instance.

        Raises:
            ValueError: If timeout or auto_stop_interval is negative.
            Exception: If workspace creation fails.

        Example:
            Create a default Python workspace:
            ```python
            workspace = daytona.create()
            ```

            Create a custom workspace:
            ```python
            params = CreateWorkspaceParams(
                language="python",
                name="my-workspace",
                image="debian:12.9",
                env_vars={"DEBUG": "true"},
                resources=WorkspaceResources(cpu=2, memory=4096),
                timeout=300,
                auto_stop_interval=0
            )
            workspace = daytona.create(params)
            ```
        """
        # If no params provided, create default params for Python
        if params is None:
            params = CreateWorkspaceParams(language="python")

        workspace_id = params.id if params.id else f"sandbox-{str(uuid.uuid4())[:8]}"
        code_toolbox = self._get_code_toolbox(params)

        try:
            if params.timeout and params.timeout < 0:
                raise ValueError("Timeout must be a non-negative number")

            if params.auto_stop_interval is not None and params.auto_stop_interval < 0:
                raise ValueError(
                    "auto_stop_interval must be a non-negative integer")

            # Create workspace using dictionary
            workspace_data = CreateWorkspace(
                id=workspace_id,
                name=params.name if params.name else workspace_id,
                image=params.image,
                user=params.os_user if params.os_user else "daytona",
                env=params.env_vars if params.env_vars else {},
                labels=params.labels,
                public=params.public,
                target=params.target if params.target else self.target,
                auto_stop_interval=params.auto_stop_interval
            )

            if params.resources:
                workspace_data.cpu = params.resources.cpu
                workspace_data.memory = params.resources.memory
                workspace_data.disk = params.resources.disk
                workspace_data.gpu = params.resources.gpu

            response = self.workspace_api.create_workspace(
                create_workspace=workspace_data)
            workspace = Workspace(
                workspace_id,
                response,
                self.workspace_api,
                self.toolbox_api,
                code_toolbox
            )

            # Wait for workspace to start
            try:
                workspace.wait_for_workspace_start(params.timeout)
            finally:
                # If not Daytona SaaS, we don't need to handle pulling image state
                pass

            return workspace

        except Exception as e:
            try:
                self.workspace_api.remove_workspace(workspace_id=workspace_id)
            except:
                pass
            raise Exception(f"Failed to create workspace: {str(e)}") from e

    def _get_code_toolbox(self, params: Optional[CreateWorkspaceParams] = None):
        """Helper method to get the appropriate code toolbox based on language.

        Args:
            params (Optional[CreateWorkspaceParams]): Workspace parameters. If not provided, defaults to Python toolbox.

        Returns:
            The appropriate code toolbox instance for the specified language.

        Raises:
            ValueError: If an unsupported language is specified.
        """
        if not params:
            return WorkspacePythonCodeToolbox()

        match params.language:
            case "javascript" | "typescript":
                return WorkspaceTsCodeToolbox()
            case "python":
                return WorkspacePythonCodeToolbox()
            case _:
                raise ValueError(f"Unsupported language: {params.language}")

    def remove(self, workspace: Workspace) -> None:
        """Removes a workspace.

        Args:
            workspace (Workspace): The workspace instance to remove.

        Example:
            ```python
            workspace = daytona.create()
            # ... use workspace ...
            daytona.remove(workspace)  # Clean up when done
            ```
        """
        return self.workspace_api.delete_workspace(workspace_id=workspace.id, force=True)

    def get_current_workspace(self, workspace_id: str) -> Workspace:
        """Get a workspace by its ID.

        Args:
            workspace_id (str): The ID of the workspace to retrieve.

        Returns:
            Workspace: The workspace instance.

        Raises:
            ValueError: If workspace_id is not provided.

        Example:
            ```python
            workspace = daytona.get_current_workspace("my-workspace-id")
            print(workspace.status)
            ```
        """
        if not workspace_id:
            raise ValueError("workspace_id is required")

        # Get the workspace instance
        workspace_instance = self.workspace_api.get_workspace(
            workspace_id=workspace_id)

        # Create and return workspace with Python code toolbox as default
        code_toolbox = WorkspacePythonCodeToolbox()
        return Workspace(
            workspace_id,
            workspace_instance,
            self.workspace_api,
            self.toolbox_api,
            code_toolbox
        )

    def list(self) -> List[Workspace]:
        """List all workspaces.

        Returns:
            List[Workspace]: List of all available workspace instances.

        Example:
            ```python
            workspaces = daytona.list()
            for workspace in workspaces:
                print(f"{workspace.id}: {workspace.status}")
            ```
        """
        workspaces = self.workspace_api.list_workspaces()
        return [
            Workspace(
                workspace.id,
                workspace,
                self.workspace_api,
                self.toolbox_api,
                self._get_code_toolbox(
                    CreateWorkspaceParams(
                        language=self._validate_language_label(
                            workspace.labels.get("code-toolbox-language"))
                    )
                )
            )
            for workspace in workspaces
        ]

    def _validate_language_label(self, language: Optional[str]) -> CodeLanguage:
        """Validate and normalize the language label.

        Args:
            language (Optional[str]): The language label to validate.

        Returns:
            CodeLanguage: The validated language, defaults to "python" if None

        Raises:
            ValueError: If the language is not supported.
        """
        if not language:
            return "python"

        if language not in ["python", "javascript", "typescript"]:
            raise ValueError(f"Invalid code-toolbox-language: {language}")

        return language  # type: ignore

    def start(self, workspace: Workspace, timeout: Optional[float] = None) -> None:
        """Starts a workspace and waits for it to be ready.

        Args:
            workspace (Workspace): The workspace to start.
            timeout (Optional[float]): Optional timeout in seconds to wait for the workspace to start. If set to 0, it will wait indefinitely.

        Example:
            ```python
            workspace = daytona.get_current_workspace("my-workspace-id")
            daytona.start(workspace, timeout=40)  # Wait up to 40 seconds
            ```
        """
        workspace.start(timeout)
        workspace.wait_for_workspace_start()

    def stop(self, workspace: Workspace) -> None:
        """Stops a workspace and waits for it to be stopped.

        Args:
            workspace (Workspace): The workspace to stop.

        Example:
            ```python
            workspace = daytona.get_current_workspace("my-workspace-id")
            daytona.stop(workspace)
            ```
        """
        workspace.stop()
        workspace.wait_for_workspace_stop()


# Export these at module level
__all__ = [
    "Daytona",
    "DaytonaConfig",
    "CreateWorkspaceParams",
    "CodeLanguage",
    "Workspace",
    "SessionExecuteRequest",
    "SessionExecuteResponse"
]
