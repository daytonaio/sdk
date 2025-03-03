import base64
from typing import Optional
from ..common.code_run_params import CodeRunParams


class WorkspacePythonCodeToolbox:
    def get_run_command(self, code: str, params: Optional[CodeRunParams] = None) -> str:
        # Encode the provided code in base64
        base64_code = base64.b64encode(code.encode()).decode()

        # Build environment variables string
        env_vars = ""
        if params and params.env:
            env_vars = ' '.join(f"{key}='{value}'" for key, value in params.env.items())

        # Build command-line arguments string
        argv = ""
        if params and params.argv:
            argv = ' '.join(params.argv)

        # Combine everything into the final command
        return f""" sh -c '{env_vars} python3 -c "exec(__import__(\\\"base64\\\").b64decode(\\\"{base64_code}\\\").decode())" {argv}' """
