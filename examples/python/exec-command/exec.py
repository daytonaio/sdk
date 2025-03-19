from daytona_sdk import Daytona, CreateWorkspaceParams, DaytonaConfig

config = DaytonaConfig(
    api_key="dtn_4d44f11c9fafdcad24a0518dffec61eef80a406b73a62bc1898e4a3854cf3d77",
    server_url="https://stage.daytona.work/api",
    target="eu"
)

daytona = Daytona(config)

daytona = Daytona(config)

params = CreateSandboxParams(
    language="python",
)
sandbox = daytona.create(params)

# Run the code securely inside the sandbox
response = sandbox.process.code_run('print("Hello World!")')
if response.exit_code != 0:
    print(f"Error: {response.exit_code} {response.result}")
else:
    print(response.result)

# Execute an os command in the sandbox
response = sandbox.process.exec('echo "Hello World from exec!"', cwd="/home/daytona", timeout=10)
if response.exit_code != 0:
    print(f"Error: {response.exit_code} {response.result}")
else:
    print(response.result)

daytona.remove(sandbox)
