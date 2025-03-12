from typing import Dict, List, Optional
from daytona_api_client import ExecuteResponse as ClientExecuteResponse
from ..charts import Chart
from pydantic import BaseModel

class ExecutionArtifacts(BaseModel):
    stdout: str
    charts: Optional[List[Chart]] = None

    def __init__(self, stdout: str = "", charts: Optional[List[Chart]] = None):
        super().__init__(stdout=stdout, charts=charts)


class ExecuteResponse(ClientExecuteResponse):
    """Response from executing a command, with additional chart handling capabilities."""
    artifacts: Optional[ExecutionArtifacts] = None

    def __init__(self, exit_code: int, result: str, artifacts: Optional[ExecutionArtifacts] = None, additional_properties: Dict = None):
        """
        Initialize an ExecuteResponse.

        Args:
            exit_code: The exit code from the command execution
            result: The output from the command execution
            artifacts: The artifacts from the command execution
            additional_properties: Additional properties from the execution
        """
        super().__init__(
            exit_code=exit_code,
            result=result,
            additional_properties=additional_properties or {}
        )
        self.artifacts = artifacts
