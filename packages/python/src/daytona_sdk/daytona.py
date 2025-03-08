"""
Sandboxes are isolated development environments managed by Daytona.
This guide covers how to create, manage, and remove Sandboxes using the SDK.

Examples:
    Basic usage with environment variables:
    ```python
    from daytona_sdk import Daytona
    # Initialize using environment variables
    daytona = Daytona()  # Uses env vars DAYTONA_API_KEY, DAYTONA_SERVER_URL, DAYTONA_TARGET
    
    # Create a default Python workspace with custom environment variables
    workspace = daytona.create(CreateWorkspaceParams(
        language="python",
        env_vars={"PYTHON_ENV": "development"}
    ))
    
    # Execute commands in the workspace
    response = workspace.process.execute_command('echo "Hello, World!"')
    print(response.result)
    
    # Run Python code securely inside the workspace
    response = workspace.process.code_run('print("Hello from Python!")')
    print(response.result)
    
    # Remove the workspace after use
    daytona.remove(workspace)
    ```

    Usage with explicit configuration:
    ```python
    from daytona_sdk import Daytona, DaytonaConfig, CreateWorkspaceParams, WorkspaceResources

    # Initialize with explicit configuration
    config = DaytonaConfig(
        api_key="your-api-key",
        server_url="https://your-server.com",
        target="us"
    )
    daytona = Daytona(config)
    
    # Create a custom workspace with specific resources and settings
    workspace = daytona.create(CreateWorkspaceParams(
        language="python",
        image="python:3.11",
        resources=WorkspaceResources(
            cpu=2,
            memory=4,  # 4GB RAM
            disk=20    # 20GB disk
        ),
        env_vars={"PYTHON_ENV": "development"},
        auto_stop_interval=60  # Auto-stop after 1 hour of inactivity
    ))
    
    # Use workspace features
    workspace.git.clone("https://github.com/user/repo.git")
    workspace.process.execute_command("python -m pytest")
    ```
"""

from enum import Enum
import uuid
from typing import Optional, Dict, List, Annotated
from pydantic import BaseModel, Field
from dataclasses import dataclass
from environs import Env
from daytona_api_client import (
    Configuration,
    WorkspaceApi,
    ToolboxApi,
    ApiClient,
    CreateWorkspace,
    SessionExecuteRequest,
    SessionExecuteResponse
)
from daytona_sdk._utils.errors import intercept_errors, DaytonaError
from .code_toolbox.workspace_python_code_toolbox import WorkspacePythonCodeToolbox
from .code_toolbox.workspace_ts_code_toolbox import WorkspaceTsCodeToolbox
from ._utils.enum import to_enum
from .workspace import Workspace, WorkspaceTargetRegion
from ._utils.timeout import with_timeout


@dataclass
class CodeLanguage(Enum):
    """Programming languages supported by Daytona"""
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)


@dataclass
class DaytonaConfig:
    """Configuration options for initializing the Daytona client.

    Attributes:
        api_key (str): API key for authentication with Daytona server.
        server_url (str): URL of the Daytona server.
        target (str): Target environment for Sandbox.

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
    target: WorkspaceTargetRegion


@dataclass
class WorkspaceResources:
    """Resources configuration for Sandbox.

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


class CreateWorkspaceParams(BaseModel):
    """Parameters for creating a new Sandbox.

    Attributes:
        language (CodeLanguage): Programming language for the Sandbox ("python", "javascript", "typescript").
        id (Optional[str]): Custom identifier for the Sandbox. If not provided, a random ID will be generated.
        name (Optional[str]): Display name for the Sandbox. Defaults to Sandbox ID if not provided.
        image (Optional[str]): Custom Docker image to use for the Sandbox.
        os_user (Optional[str]): OS user for the Sandbox. Defaults to "daytona".
        env_vars (Optional[Dict[str, str]]): Environment variables to set in the Sandbox.
        labels (Optional[Dict[str, str]]): Custom labels for the Sandbox.
        public (Optional[bool]): Whether the Sandbox should be public.
        target (Optional[str]): Target location for the Sandbox. Can be "us", "eu", or "asia".
        resources (Optional[WorkspaceResources]): Resource configuration for the Sandbox.
        timeout (Optional[float]): Timeout in seconds for Sandbox to be created and started.
        auto_stop_interval (Optional[int]): Interval in minutes after which Sandbox will automatically stop if no Sandbox event occurs during that time. Default is 15 minutes. 0 means no auto-stop.

    Example:
        ```python
        params = CreateWorkspaceParams(
            language="python",
            name="my-workspace",
            env_vars={"DEBUG": "true"},
            resources=WorkspaceResources(cpu=2, memory=4),
            auto_stop_interval=20
        )
        workspace = daytona.create(params, 50)
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
    target: Optional[WorkspaceTargetRegion] = None
    resources: Optional[WorkspaceResources] = None
    timeout: Annotated[Optional[float], Field(
        default=None, deprecated='The `timeout` field is deprecated and will be removed in future versions. Use `timeout` argument in method calls instead.')]
    auto_stop_interval: Optional[int] = None


class Daytona:
    """Main class for interacting with Daytona Server API.

    This class provides methods to create, manage, and interact with Daytona Sandboxes.
    It can be initialized either with explicit configuration or using environment variables.

    Attributes:
        api_key (str): API key for authentication.
        server_url (str): URL of the Daytona server.
        target (str): Default target location for Sandboxes.

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
        """Initializes Daytona instance with optional configuration.

        If no config is provided, reads from environment variables:
        - `DAYTONA_API_KEY`: Required API key for authentication
        - `DAYTONA_SERVER_URL`: Required server URL
        - `DAYTONA_TARGET`: Optional target environment (defaults to WorkspaceTargetRegion.US)

        Args:
            config (Optional[DaytonaConfig]): Object containing api_key, server_url, and target.

        Raises:
            DaytonaError: If API key or Server URL is not provided either through config or environment variables

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
            self.target = env.str("DAYTONA_TARGET", WorkspaceTargetRegion.US)
        else:
            self.api_key = config.api_key
            self.server_url = config.server_url
            self.target = config.target

        if not self.api_key:
            raise DaytonaError("API key is required")

        if not self.server_url:
            raise DaytonaError("Server URL is required")

        if not self.target:
            self.target = WorkspaceTargetRegion.US

        # Create API configuration without api_key
        configuration = Configuration(host=self.server_url)
        api_client = ApiClient(configuration)
        api_client.default_headers["Authorization"] = f"Bearer {self.api_key}"

        # Initialize API clients with the api_client instance
        self.workspace_api = WorkspaceApi(api_client)
        self.toolbox_api = ToolboxApi(api_client)

    @intercept_errors(message_prefix="Failed to create workspace: ")
    def create(self, params: Optional[CreateWorkspaceParams] = None, timeout: Optional[float] = 60) -> Workspace:
        """Creates Sandboxes with default or custom configurations. You can specify various parameters,
        including language, image, resources, environment variables, and volumes for the Sandbox.

        Args:
            params (Optional[CreateWorkspaceParams]): Parameters for Sandbox creation. If not provided,
                   defaults to Python language.
            timeout (Optional[float]): Timeout (in seconds) for workspace creation. 0 means no timeout. Default is 60 seconds.

        Returns:
            Workspace: The created Sandbox instance.

        Raises:
            DaytonaError: If timeout or auto_stop_interval is negative; If workspace fails to start or times out

        Example:
            Create a default Python Sandbox:
            ```python
            workspace = daytona.create()
            ```

            Create a custom Sandbox:
            ```python
            params = CreateWorkspaceParams(
                language="python",
                name="my-workspace",
                image="debian:12.9",
                env_vars={"DEBUG": "true"},
                resources=WorkspaceResources(cpu=2, memory=4096),
                auto_stop_interval=0
            )
            workspace = daytona.create(params, 40)
            ```
        """
        # If no params provided, create default params for Python
        if params is None:
            params = CreateWorkspaceParams(language="python")

        params.id = params.id if params.id else f"sandbox-{str(uuid.uuid4())[:8]}"

        effective_timeout = params.timeout if params.timeout else timeout

        try:
            return self._create(params, effective_timeout)
        except Exception as e:
            try:
                self.workspace_api.delete_workspace(
                    workspace_id=params.id, force=True)
            except Exception:
                pass
            raise e

    @with_timeout(error_message=lambda self, timeout: f"Failed to create and start workspace within {timeout} seconds timeout period.")
    def _create(self, params: Optional[CreateWorkspaceParams] = None, timeout: Optional[float] = 60) -> Workspace:
        """Creates a new Sandbox and waits for it to start.

        Args:
            params (Optional[CreateWorkspaceParams]): Parameters for Sandbox creation. If not provided,
                   defaults to Python language.
            timeout (Optional[float]): Timeout (in seconds) for workspace creation. 0 means no timeout. Default is 60 seconds.

        Returns:
            Workspace: The created Sandbox instance.

        Raises:
            DaytonaError: If timeout or auto_stop_interval is negative; If workspace fails to start or times out
        """
        code_toolbox = self._get_code_toolbox(params)

        if timeout < 0:
            raise DaytonaError("Timeout must be a non-negative number")

        if params.auto_stop_interval is not None and params.auto_stop_interval < 0:
            raise DaytonaError(
                "auto_stop_interval must be a non-negative integer")

        target = params.target if params.target else self.target

        # Create workspace using dictionary
        workspace_data = CreateWorkspace(
            id=params.id,
            name=params.name if params.name else params.id,
            image=params.image,
            user=params.os_user if params.os_user else "daytona",
            env=params.env_vars if params.env_vars else {},
            labels=params.labels,
            public=params.public,
            target=str(target) if target else None,
            auto_stop_interval=params.auto_stop_interval
        )

        if params.resources:
            workspace_data.cpu = params.resources.cpu
            workspace_data.memory = params.resources.memory
            workspace_data.disk = params.resources.disk
            workspace_data.gpu = params.resources.gpu

        response = self.workspace_api.create_workspace(
            create_workspace=workspace_data, _request_timeout=timeout or None)
        workspace_info = Workspace._to_workspace_info(response)
        response.info = workspace_info

        workspace = Workspace(
            params.id,
            response,
            self.workspace_api,
            self.toolbox_api,
            code_toolbox
        )

        # Wait for workspace to start
        try:
            workspace.wait_for_workspace_start()
        finally:
            # If not Daytona SaaS, we don't need to handle pulling image state
            pass

        return workspace

    def _get_code_toolbox(self, params: Optional[CreateWorkspaceParams] = None):
        """Helper method to get the appropriate code toolbox based on language.

        Args:
            params (Optional[CreateWorkspaceParams]): Sandbox parameters. If not provided, defaults to Python toolbox.

        Returns:
            The appropriate code toolbox instance for the specified language.

        Raises:
            DaytonaError: If an unsupported language is specified.
        """
        if not params:
            return WorkspacePythonCodeToolbox()

        enum_language = to_enum(CodeLanguage, params.language)
        if enum_language is None:
            raise DaytonaError(f"Unsupported language: {params.language}")
        else:
            params.language = enum_language

        match params.language:
            case CodeLanguage.JAVASCRIPT | CodeLanguage.TYPESCRIPT:
                return WorkspaceTsCodeToolbox()
            case CodeLanguage.PYTHON:
                return WorkspacePythonCodeToolbox()
            case _:
                raise DaytonaError(f"Unsupported language: {params.language}")

    @intercept_errors(message_prefix="Failed to remove workspace: ")
    def remove(self, workspace: Workspace, timeout: Optional[float] = 60) -> None:
        """Removes a Sandbox.

        Args:
            workspace (Workspace): The Sandbox instance to remove.
            timeout (Optional[float]): Timeout (in seconds) for workspace removal. 0 means no timeout. Default is 60 seconds.

        Raises:
            DaytonaError: If workspace fails to remove or times out

        Example:
            ```python
            workspace = daytona.create()
            # ... use workspace ...
            daytona.remove(workspace)  # Clean up when done
            ```
        """
        return self.workspace_api.delete_workspace(workspace_id=workspace.id, force=True, _request_timeout=timeout or None)

    @intercept_errors(message_prefix="Failed to get workspace: ")
    def get_current_workspace(self, workspace_id: str) -> Workspace:
        """Get a Sandbox by its ID.

        Args:
            workspace_id (str): The ID of the Sandbox to retrieve.

        Returns:
            Workspace: The Sandbox instance.

        Raises:
            DaytonaError: If workspace_id is not provided.

        Example:
            ```python
            workspace = daytona.get_current_workspace("my-workspace-id")
            print(workspace.status)
            ```
        """
        if not workspace_id:
            raise DaytonaError("workspace_id is required")

        # Get the workspace instance
        workspace_instance = self.workspace_api.get_workspace(
            workspace_id=workspace_id)
        workspace_info = Workspace._to_workspace_info(workspace_instance)
        workspace_instance.info = workspace_info

        # Create and return workspace with Python code toolbox as default
        code_toolbox = WorkspacePythonCodeToolbox()
        return Workspace(
            workspace_id,
            workspace_instance,
            self.workspace_api,
            self.toolbox_api,
            code_toolbox
        )

    @intercept_errors(message_prefix="Failed to list workspaces: ")
    def list(self) -> List[Workspace]:
        """Lists all Sandboxes.

        Returns:
            List[Workspace]: List of all available Sandbox instances.

        Example:
            ```python
            workspaces = daytona.list()
            for workspace in workspaces:
                print(f"{workspace.id}: {workspace.status}")
            ```
        """
        workspaces = self.workspace_api.list_workspaces()

        for workspace in workspaces:
            workspace_info = Workspace._to_workspace_info(workspace)
            workspace.info = workspace_info

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
        """Validates and normalizes the language label.

        Args:
            language (Optional[str]): The language label to validate.

        Returns:
            CodeLanguage: The validated language, defaults to "python" if None

        Raises:
            DaytonaError: If the language is not supported.
        """
        if not language:
            return CodeLanguage.PYTHON

        enum_language = to_enum(CodeLanguage, language)
        if enum_language is None:
            raise DaytonaError(f"Invalid code-toolbox-language: {language}")
        else:
            return enum_language

    # def resize(self, workspace: Workspace, resources: WorkspaceResources) -> None:
    #     """Resizes a workspace.

    #     Args:
    #         workspace: The workspace to resize
    #         resources: The new resources to set
    #     """
    #     self.workspace_api. (workspace_id=workspace.id, resources=resources)

    def start(self, workspace: Workspace, timeout: Optional[float] = 60) -> None:
        """Starts a Sandbox and waits for it to be ready.

        Args:
            workspace (Workspace): The Sandbox to start.
            timeout (Optional[float]): Optional timeout in seconds to wait for the Sandbox to start. 0 means no timeout. Default is 60 seconds.

        Raises:
            DaytonaError: If timeout is negative; If Sandbox fails to start or times out
        """
        workspace.start(timeout)

    def stop(self, workspace: Workspace, timeout: Optional[float] = 60) -> None:
        """Stops a Sandbox and waits for it to be stopped.

        Args:
            workspace (Workspace): The workspace to stop
            timeout (Optional[float]): Optional timeout (in seconds) for workspace stop. 0 means no timeout. Default is 60 seconds.

        Raises:
            DaytonaError: If timeout is negative; If Sandbox fails to stop or times out
        """
        workspace.stop(timeout)


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
