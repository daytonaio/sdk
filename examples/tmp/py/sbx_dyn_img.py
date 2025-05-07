from daytona_sdk import CreateSandboxParams, Daytona, Image

image = (
    Image.base("python:3.13.2-slim-bookworm").pip_install(["ruff", "black", "numpy", "pandas", "matplotlib", "seaborn"])
    # .pip_install_from_pyproject("packages/python/pyproject.toml", optional_dependencies=["dev"])
    # .run_commands("mkdir -p /home/daytona/ws")
    # .workdir("/home/daytona/ws")
    # .add_local_dir("packages/python", "/home/daytona/ws/python-pkg")
)

daytona = Daytona()

sandbox = daytona.create(
    CreateSandboxParams(
        image=image,
        auto_stop_interval=0,
        os_user="root",
    ),
    timeout=0,
    on_image_build_logs=print,
)

response = sandbox.process.exec("pip list")
print("command: pip list")
print(response.result)

response = sandbox.process.exec("ls -la")
print("command: ls -la")
print(response.result)

response = sandbox.process.exec("pwd")
print("command: pwd")
print(response.result)

response = sandbox.process.exec("whoami")
print("command: whoami")
print(response.result)

daytona.remove(sandbox)
