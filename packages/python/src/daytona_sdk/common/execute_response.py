from typing import Dict, List, Optional

from daytona_api_client import ExecuteResponse as ClientExecuteResponse
from pydantic import ConfigDict

from ..charts import Chart


class ExecutionArtifacts:
    stdout: str
    charts: Optional[List[Chart]] = None

    def __init__(self, stdout: str = "", charts: Optional[List[Chart]] = None):
        self.stdout = stdout
        self.charts = charts


class ExecuteResponse(ClientExecuteResponse):
    """Response from executing a command, with additional chart handling capabilities."""

    artifacts: Optional[ExecutionArtifacts] = None

    # TODO: Remove model_config once everything is migrated to pydantic # pylint: disable=fixme
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # pylint: disable=super-init-not-called
    def __init__(
        self,
        exit_code: int,
        result: str,
        artifacts: Optional[ExecutionArtifacts] = None,
        additional_properties: Dict = None,
    ):
        """
        Initialize an ExecuteResponse.

        Args:
            exit_code: The exit code from the command execution
            result: The output from the command execution
            artifacts: The artifacts from the command execution
            additional_properties: Additional properties from the execution
        """
        self.exit_code = exit_code
        self.result = result
        self.additional_properties = additional_properties or {}
        self.artifacts = artifacts
