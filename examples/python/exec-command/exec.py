from daytona_sdk import CreateSandboxParams, Daytona, Image

daytona = Daytona()

image = Image.from_dockerfile("/home/daytona/daytona-ai-saas/Dockerfile").set_name("test-image:0.0.5").set_propagate()
daytona.build_image(image)

params = CreateSandboxParams(
    os_user='root',
    image="test-image:0.0.5",
)
sandbox = daytona.create(params, timeout=0)

# Run the code securely inside the sandbox
response = sandbox.process.code_run('print("Hello World!")')
if response.exit_code != 0:
    print(f"Error: {response.exit_code} {response.result}")
else:
    print(response.result)

# Execute an os command in the sandbox
response = sandbox.process.exec(
    'echo "Hello World from exec!"', cwd="/home/daytona", timeout=10)
if response.exit_code != 0:
    print(f"Error: {response.exit_code} {response.result}")
else:
    print(response.result)

# daytona.remove(sandbox)
