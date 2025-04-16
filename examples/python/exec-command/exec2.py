from daytona_sdk import CreateSandboxParams, Daytona, Image

daytona = Daytona()

sandbox = daytona.get_current_sandbox("sandbox-ff7a8922")

response = sandbox.process.exec("ls -la /app/apps")

print(response.result)