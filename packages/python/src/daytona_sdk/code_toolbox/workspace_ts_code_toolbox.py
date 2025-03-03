import base64
from typing import Optional
from ..common.code_run_params import CodeRunParams


class WorkspaceTsCodeToolbox:
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

        # Combine everything into the final command for TypeScript
        return f""" sh -c 'echo {base64_code} | base64 --decode | {env_vars} npx ts-node -O "{{\\\"module\\\":\\\"CommonJS\\\"}}" -e "$(cat)" x {argv} 2>&1 | grep -vE "npm notice|npm warn exec"' """
