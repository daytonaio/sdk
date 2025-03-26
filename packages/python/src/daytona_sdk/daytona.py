"""
Sandboxes are isolated development environments managed by Daytona.
This guide covers how to create, manage, and remove Sandboxes using the SDK.

Examples:
    Basic usage with environment variables:
    ```python
    from daytona_sdk import Daytona
    # Initialize using environment variables
    daytona = Daytona()  # Uses env vars DAYTONA_API_KEY, DAYTONA_SERVER_URL, DAYTONA_TARGET

    # Create a default Python sandbox with custom environment variables
    sandbox = daytona.create(CreateSandboxParams(
        language="python",
        env_vars={"PYTHON_ENV": "development"}
    ))

    # Execute commands in the sandbox
    response = sandbox.process.execute_command('echo "Hello, World!"')
    print(response.result)

    # Run Python code securely inside the sandbox
    response = sandbox.process.code_run('print("Hello from Python!")')
    print(response.result)

    # Remove the sandbox after use
    daytona.remove(sandbox)
    ```

    Usage with explicit configuration:
    ```python
    from daytona_sdk import Daytona, DaytonaConfig, CreateSandboxParams, SandboxResources

    # Initialize with explicit configuration
    config = DaytonaConfig(
        api_key="your-api-key",
        server_url="https://your-server.com",
        target="us"
    )
    daytona = Daytona(config)

    # Create a custom sandbox with specific resources and settings
    sandbox = daytona.create(CreateSandboxParams(
        language="python",
        image="python:3.11",
        resources=SandboxResources(
            cpu=2,
            memory=4,  # 4GB RAM
            disk=20    # 20GB disk
        ),
        env_vars={"PYTHON_ENV": "development"},
        auto_stop_interval=60  # Auto-stop after 1 hour of inactivity
    ))

    # Use sandbox features
    sandbox.git.clone("https://github.com/user/repo.git")
    sandbox.process.execute_command("python -m pytest")
    ```
"""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Dict, List, Optional

from daytona_api_client import ApiClient, Configuration
from daytona_api_client import CreateWorkspace as CreateSandbox
from daytona_api_client import SessionExecuteRequest, SessionExecuteResponse, ToolboxApi
from daytona_api_client import WorkspaceApi as SandboxApi
from daytona_sdk._utils.errors import DaytonaError, intercept_errors
from deprecated import deprecated
from environs import Env
from pydantic import BaseModel, Field

from ._utils.enum import to_enum
from ._utils.timeout import with_timeout
from .code_toolbox.sandbox_python_code_toolbox import SandboxPythonCodeToolbox
from .code_toolbox.sandbox_ts_code_toolbox import SandboxTsCodeToolbox
from .sandbox import Sandbox, SandboxTargetRegion

Workspace = Sandbox


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
        api_key (Optional[str]): API key for authentication with Daytona server. If not set, it must be provided
        as environment variable DAYTONA_API_KEY.
        server_url (Optional[str]): URL of the Daytona server. Defaults to 'https://app.daytona.io/api' if not set.
        target (Optional[SandboxTargetRegion]): Target environment for Sandbox. Defaults to 'us' if not set.

    Example:
        ```python
        # Only API key is required
        config = DaytonaConfig(api_key="your-api-key")
        ```
    """

    api_key: Optional[str] = None
    server_url: Optional[str] = None
    target: Optional[SandboxTargetRegion] = None


@dataclass
class SandboxResources:
    """Resources configuration for Sandbox.

    Attributes:
        cpu (Optional[int]): Number of CPU cores to allocate.
        memory (Optional[int]): Amount of memory in GB to allocate.
        disk (Optional[int]): Amount of disk space in GB to allocate.
        gpu (Optional[int]): Number of GPUs to allocate.

    Example:
        ```python
        resources = SandboxResources(
            cpu=2,
            memory=4,  # 4GB RAM
            disk=20,   # 20GB disk
            gpu=1
        )
        params = CreateSandboxParams(
            language="python",
            resources=resources
        )
        ```
    """

    cpu: Optional[int] = None
    memory: Optional[int] = None
    disk: Optional[int] = None
    gpu: Optional[int] = None


class CreateSandboxParams(BaseModel):
    """Parameters for creating a new Sandbox.

    Attributes:
        language (Optional[CodeLanguage]): Programming language for the Sandbox ("python", "javascript", "typescript").
        Defaults to "python".
        id (Optional[str]): Custom identifier for the Sandbox. If not provided, a random ID will be generated.
        name (Optional[str]): Display name for the Sandbox. Defaults to Sandbox ID if not provided.
        image (Optional[str]): Custom Docker image to use for the Sandbox.
        os_user (Optional[str]): OS user for the Sandbox.
        env_vars (Optional[Dict[str, str]]): Environment variables to set in the Sandbox.
        labels (Optional[Dict[str, str]]): Custom labels for the Sandbox.
        public (Optional[bool]): Whether the Sandbox should be public.
        target (Optional[str]): Target location for the Sandbox. Can be "us", "eu", or "asia".
        resources (Optional[SandboxResources]): Resource configuration for the Sandbox.
        timeout (Optional[float]): Timeout in seconds for Sandbox to be created and started.
        auto_stop_interval (Optional[int]): Interval in minutes after which Sandbox will
            automatically stop if no Sandbox event occurs during that time. Default is 15 minutes.
            0 means no auto-stop.

    Example:
        ```python
        params = CreateSandboxParams(
            language="python",
            name="my-sandbox",
            env_vars={"DEBUG": "true"},
            resources=SandboxResources(cpu=2, memory=4),
            auto_stop_interval=20
        )
        sandbox = daytona.create(params, 50)
        ```
    """

    language: Optional[CodeLanguage] = None
    id: Optional[str] = None
    name: Optional[str] = None
    image: Optional[str] = None
    os_user: Optional[str] = None
    env_vars: Optional[Dict[str, str]] = None
    labels: Optional[Dict[str, str]] = None
    public: Optional[bool] = None
    target: Optional[SandboxTargetRegion] = None
    resources: Optional[SandboxResources] = None
    timeout: Annotated[
        Optional[float],
        Field(
            default=None,
            deprecated=(
                "The `timeout` field is deprecated and will be removed in future versions. "
                "Use `timeout` argument in method calls instead."
            ),
        ),
    ]
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
        - `DAYTONA_TARGET`: Optional target environment (defaults to SandboxTargetRegion.US)

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

        default_server_url = "https://app.daytona.io/api"
        default_target = SandboxTargetRegion.US
        self.default_language = CodeLanguage.PYTHON

        if config is None or None in [config.api_key, config.server_url, config.target]:
            # Initialize env - it automatically reads from .env and .env.local
            env = Env()
            env.read_env()  # reads .env
            # reads .env.local and overrides values
            env.read_env(".env.local", override=True)

            self.api_key = env.str("DAYTONA_API_KEY", None)
            self.server_url = env.str("DAYTONA_SERVER_URL", default_server_url)
            self.target = env.str("DAYTONA_TARGET", default_target)

        if config:
            self.api_key = config.api_key or self.api_key
            self.server_url = config.server_url or self.server_url
            self.target = config.target or self.target

        if not self.api_key:
            raise DaytonaError("API key is required")

        # Create API configuration without api_key
        configuration = Configuration(host=self.server_url)
        api_client = ApiClient(configuration)
        api_client.default_headers["Authorization"] = f"Bearer {self.api_key}"

        # Initialize API clients with the api_client instance
        self.sandbox_api = SandboxApi(api_client)
        self.toolbox_api = ToolboxApi(api_client)

    @intercept_errors(message_prefix="Failed to create sandbox: ")
    def create(
        self,
        params: Optional[CreateSandboxParams] = None,
        timeout: Optional[float] = 60,
    ) -> Sandbox:
        """Creates Sandboxes with default or custom configurations. You can specify various parameters,
        including language, image, resources, environment variables, and volumes for the Sandbox.

        Args:
            params (Optional[CreateSandboxParams]): Parameters for Sandbox creation. If not provided,
                   defaults to Python language.
            timeout (Optional[float]): Timeout (in seconds) for sandbox creation. 0 means no timeout.
                Default is 60 seconds.

        Returns:
            Sandbox: The created Sandbox instance.

        Raises:
            DaytonaError: If timeout or auto_stop_interval is negative; If sandbox fails to start or times out

        Example:
            Create a default Python Sandbox:
            ```python
            sandbox = daytona.create()
            ```

            Create a custom Sandbox:
            ```python
            params = CreateSandboxParams(
                language="python",
                name="my-sandbox",
                image="debian:12.9",
                env_vars={"DEBUG": "true"},
                resources=SandboxResources(cpu=2, memory=4096),
                auto_stop_interval=0
            )
            sandbox = daytona.create(params, 40)
            ```
        """
        # If no params provided, create default params for Python
        if params is None:
            params = CreateSandboxParams(language=self.default_language)
        if params.language is None:
            params.language = self.default_language

        effective_timeout = params.timeout if params.timeout else timeout

        try:
            return self._create(params, effective_timeout)
        except Exception as e:
            try:
                self.sandbox_api.delete_workspace(params.id, force=True)
            except Exception:
                pass
            raise e

    @with_timeout(
        error_message=lambda self, timeout: (
            f"Failed to create and start sandbox within {timeout} seconds timeout period."
        )
    )
    def _create(
        self,
        params: Optional[CreateSandboxParams] = None,
        timeout: Optional[float] = 60,
    ) -> Sandbox:
        """Creates a new Sandbox and waits for it to start.

        Args:
            params (Optional[CreateSandboxParams]): Parameters for Sandbox creation. If not provided,
                   defaults to Python language.
            timeout (Optional[float]): Timeout (in seconds) for sandbox creation. 0 means no timeout.
                Default is 60 seconds.

        Returns:
            Sandbox: The created Sandbox instance.

        Raises:
            DaytonaError: If timeout or auto_stop_interval is negative; If sandbox fails to start or times out
        """
        code_toolbox = self._get_code_toolbox(params)

        if timeout < 0:
            raise DaytonaError("Timeout must be a non-negative number")

        if params.auto_stop_interval is not None and params.auto_stop_interval < 0:
            raise DaytonaError("auto_stop_interval must be a non-negative integer")

        target = params.target if params.target else self.target

        # Create sandbox using dictionary
        sandbox_data = CreateSandbox(
            id=params.id,
            name=params.name if params.name else params.id,
            image=params.image,
            user=params.os_user,
            env=params.env_vars if params.env_vars else {},
            labels=params.labels,
            public=params.public,
            target=str(target) if target else None,
            auto_stop_interval=params.auto_stop_interval,
        )

        if params.resources:
            sandbox_data.cpu = params.resources.cpu
            sandbox_data.memory = params.resources.memory
            sandbox_data.disk = params.resources.disk
            sandbox_data.gpu = params.resources.gpu

        response = self.sandbox_api.create_workspace(sandbox_data, _request_timeout=timeout or None)
        sandbox_info = Sandbox.to_sandbox_info(response)
        response.info = sandbox_info

        sandbox = Sandbox(
            response.id,
            response,
            self.sandbox_api,
            self.toolbox_api,
            code_toolbox,
        )

        # # Wait for sandbox to start
        # try:
        #     sandbox.wait_for_sandbox_start()
        # finally:
        #     # If not Daytona SaaS, we don't need to handle pulling image state
        #     pass

        return sandbox

    def _get_code_toolbox(self, params: Optional[CreateSandboxParams] = None):
        """Helper method to get the appropriate code toolbox based on language.

        Args:
            params (Optional[CreateSandboxParams]): Sandbox parameters. If not provided, defaults to Python toolbox.

        Returns:
            The appropriate code toolbox instance for the specified language.

        Raises:
            DaytonaError: If an unsupported language is specified.
        """
        if not params:
            return SandboxPythonCodeToolbox()

        enum_language = to_enum(CodeLanguage, params.language)
        if enum_language is None:
            raise DaytonaError(f"Unsupported language: {params.language}")
        params.language = enum_language

        match params.language:
            case CodeLanguage.JAVASCRIPT | CodeLanguage.TYPESCRIPT:
                return SandboxTsCodeToolbox()
            case CodeLanguage.PYTHON:
                return SandboxPythonCodeToolbox()
            case _:
                raise DaytonaError(f"Unsupported language: {params.language}")

    @intercept_errors(message_prefix="Failed to remove sandbox: ")
    def remove(self, sandbox: Sandbox, timeout: Optional[float] = 60) -> None:
        """Removes a Sandbox.

        Args:
            sandbox (Sandbox): The Sandbox instance to remove.
            timeout (Optional[float]): Timeout (in seconds) for sandbox removal. 0 means no timeout.
                Default is 60 seconds.

        Raises:
            DaytonaError: If sandbox fails to remove or times out

        Example:
            ```python
            sandbox = daytona.create()
            # ... use sandbox ...
            daytona.remove(sandbox)  # Clean up when done
            ```
        """
        return self.sandbox_api.delete_workspace(sandbox.id, force=True, _request_timeout=timeout or None)

    @deprecated(
        reason=(
            "Method is deprecated. Use `get_current_sandbox` instead. This method will be removed in a future version."
        )
    )
    def get_current_workspace(self, workspace_id: str) -> Workspace:
        """Get a Sandbox by its ID.

        Args:
            workspace_id (str): The ID of the Sandbox to retrieve.

        Returns:
            Workspace: The Sandbox instance.
        """
        return self.get_current_sandbox(workspace_id)

    @intercept_errors(message_prefix="Failed to get sandbox: ")
    def get_current_sandbox(self, sandbox_id: str) -> Sandbox:
        """Get a Sandbox by its ID.

        Args:
            sandbox_id (str): The ID of the Sandbox to retrieve.

        Returns:
            Sandbox: The Sandbox instance.

        Raises:
            DaytonaError: If sandbox_id is not provided.

        Example:
            ```python
            sandbox = daytona.get_current_sandbox("my-sandbox-id")
            print(sandbox.status)
            ```
        """
        if not sandbox_id:
            raise DaytonaError("sandbox_id is required")

        # Get the sandbox instance
        sandbox_instance = self.sandbox_api.get_workspace(sandbox_id)
        sandbox_info = Sandbox.to_sandbox_info(sandbox_instance)
        sandbox_instance.info = sandbox_info

        # Create and return sandbox with Python code toolbox as default
        code_toolbox = SandboxPythonCodeToolbox()
        return Sandbox(
            sandbox_id,
            sandbox_instance,
            self.sandbox_api,
            self.toolbox_api,
            code_toolbox,
        )

    @intercept_errors(message_prefix="Failed to list sandboxes: ")
    def list(self) -> List[Sandbox]:
        """Lists all Sandboxes.

        Returns:
            List[Sandbox]: List of all available Sandbox instances.

        Example:
            ```python
            sandboxes = daytona.list()
            for sandbox in sandboxes:
                print(f"{sandbox.id}: {sandbox.status}")
            ```
        """
        sandboxes = self.sandbox_api.list_workspaces()

        for sandbox in sandboxes:
            sandbox_info = Sandbox.to_sandbox_info(sandbox)
            sandbox.info = sandbox_info

        return [
            Sandbox(
                sandbox.id,
                sandbox,
                self.sandbox_api,
                self.toolbox_api,
                self._get_code_toolbox(
                    CreateSandboxParams(
                        language=self._validate_language_label(sandbox.labels.get("code-toolbox-language"))
                    )
                ),
            )
            for sandbox in sandboxes
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
        return enum_language

    # def resize(self, sandbox: Sandbox, resources: SandboxResources) -> None:
    #     """Resizes a sandbox.

    #     Args:
    #         sandbox: The sandbox to resize
    #         resources: The new resources to set
    #     """
    #     self.sandbox_api. (sandbox_id=sandbox.id, resources=resources)

    def start(self, sandbox: Sandbox, timeout: Optional[float] = 60) -> None:
        """Starts a Sandbox and waits for it to be ready.

        Args:
            sandbox (Sandbox): The Sandbox to start.
            timeout (Optional[float]): Optional timeout in seconds to wait for the Sandbox to start.
                0 means no timeout. Default is 60 seconds.

        Raises:
            DaytonaError: If timeout is negative; If Sandbox fails to start or times out
        """
        sandbox.start(timeout)

    def stop(self, sandbox: Sandbox, timeout: Optional[float] = 60) -> None:
        """Stops a Sandbox and waits for it to be stopped.

        Args:
            sandbox (Sandbox): The sandbox to stop
            timeout (Optional[float]): Optional timeout (in seconds) for sandbox stop.
                0 means no timeout. Default is 60 seconds.

        Raises:
            DaytonaError: If timeout is negative; If Sandbox fails to stop or times out
        """
        sandbox.stop(timeout)


# Export these at module level
__all__ = [
    "Daytona",
    "DaytonaConfig",
    "CreateSandboxParams",
    "CodeLanguage",
    "Sandbox",
    "SessionExecuteRequest",
    "SessionExecuteResponse",
]
