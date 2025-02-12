"""
Process and code execution within a Daytona workspace.

This module provides functionality for executing commands and running code
in the workspace environment.
"""

from typing import Optional, List
from daytona_api_client import (
    ToolboxApi,
    ExecuteResponse,
    ExecuteRequest,
    Session,
    SessionExecuteRequest,
    SessionExecuteResponse,
    CreateSessionRequest,
    Command
)

from daytona_sdk._utils.exceptions import intercept_exceptions
from .code_toolbox.workspace_python_code_toolbox import WorkspacePythonCodeToolbox
from .protocols import WorkspaceInstance

class Process:
    """Handles process and code execution within a workspace.
    
    Args:
        code_toolbox: Language-specific code execution toolbox
        toolbox_api: API client for workspace operations
        instance: The workspace instance
    """

    def __init__(
        self,
        code_toolbox: WorkspacePythonCodeToolbox,
        toolbox_api: ToolboxApi,
        instance: WorkspaceInstance,
    ):
        self.code_toolbox = code_toolbox
        self.toolbox_api = toolbox_api
        self.instance = instance

    @intercept_exceptions(message_prefix="Failed to execute command: ")
    def exec(self, command: str, cwd: Optional[str] = None, timeout: Optional[int] = None) -> ExecuteResponse:
        """Executes a shell command in the workspace.
        
        Args:
            command: Command to execute
            cwd: Working directory for command execution (optional)
            timeout: Optional timeout in seconds
            
        Returns:
            Command execution results
        """
        execute_request = ExecuteRequest(
            command=command,
            cwd=cwd,
            timeout=timeout
        )
        
        return self.toolbox_api.execute_command(
            workspace_id=self.instance.id,
            execute_request=execute_request
        )

    def code_run(self, code: str) -> ExecuteResponse:
        """Executes code in the workspace using the appropriate language runtime.
        
        Args:
            code: Code to execute
            
        Returns:
            Code execution results
        """
        command = self.code_toolbox.get_run_command(code)
        return self.exec(command)

    @intercept_exceptions(message_prefix="Failed to create session: ")
    def create_session(self, session_id: str) -> None:
        """Creates a new exec session in the workspace.
        
        Args:
            session_id: Unique identifier for the session
        """
        request = CreateSessionRequest(sessionId=session_id)
        self.toolbox_api.create_session(
            workspace_id=self.instance.id,
            create_session_request=request
        )

    @intercept_exceptions(message_prefix="Failed to get session: ")
    def get_session(self, session_id: str) -> Session:
        """Gets a session in the workspace.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Session
        """
        return self.toolbox_api.get_session(
            workspace_id=self.instance.id,
            session_id=session_id
        )

    @intercept_exceptions(message_prefix="Failed to get session command: ")
    def get_session_command(self, session_id: str, command_id: str) -> Command:
        """Gets a command in the session.
        
        Args:
            session_id: Unique identifier for the session
            command_id: Unique identifier for the command
            
        Returns:
            Command
        """
        return self.toolbox_api.get_session_command(
            workspace_id=self.instance.id,
            session_id=session_id,
            command_id=command_id
        )

    @intercept_exceptions(message_prefix="Failed to execute session command: ")
    def execute_session_command(self, session_id: str, req: SessionExecuteRequest) -> SessionExecuteResponse:
        """Executes a command in the session.
        
        Args:
            session_id: Unique identifier for the session
            req: Command to execute and async flag
            
        Returns:
            Command execution results
        """
        return self.toolbox_api.execute_session_command(
            workspace_id=self.instance.id,
            session_id=session_id,
            session_execute_request=req
        )

    @intercept_exceptions(message_prefix="Failed to get session command logs: ")
    def get_session_command_logs(self, session_id: str, command_id: str) -> str:
        """Gets the logs for a command in the session.
        
        Args:
            session_id: Unique identifier for the session
            command_id: Unique identifier for the command
            
        Returns:
            Command logs
        """
        return self.toolbox_api.get_session_command_logs(
            workspace_id=self.instance.id,
            session_id=session_id,
            command_id=command_id
        )

    @intercept_exceptions(message_prefix="Failed to list sessions: ")
    def list_sessions(self) -> List[Session]:
        """Lists all sessions in the workspace.
        
        Returns:
            List of sessions
        """
        return self.toolbox_api.list_sessions(
            workspace_id=self.instance.id
        )

    @intercept_exceptions(message_prefix="Failed to delete session: ")
    def delete_session(self, session_id: str) -> None:
        """Deletes a session in the workspace.
        
        Args:
            session_id: Unique identifier for the session
        """
        self.toolbox_api.delete_session(
            workspace_id=self.instance.id,
            session_id=session_id
        )

    