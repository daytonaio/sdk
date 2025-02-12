import base64

class WorkspaceTsCodeToolbox:
    def get_run_command(self, code: str) -> str:
        base64_code = base64.b64encode(code.encode()).decode()
        return f""" sh -c 'echo {base64_code} | base64 --decode | npx ts-node --compiler-options "{{\\\"module\\\":\\\"CommonJS\\\"}}" 2>&1 | grep -vE "npm notice|npm warn exec"' """
    