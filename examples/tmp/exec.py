from daytona_sdk import CreateSandboxParams, Daytona, VolumeMount

daytona = Daytona()
sandboxes = daytona.list()
print(sandboxes)
volume = daytona.volume.get("test-volume-py")  # daytona.volume.create("test-volume-py")

sandbox1 = daytona.create(
    CreateSandboxParams(volumes=[VolumeMount(volume_id=volume.id, mount_path="/home/daytona/volume-dir")])
)
response = sandbox1.process.exec('echo "Hello World from exec!" > /home/daytona/volume-dir/test.txt')
if response.exit_code != 0:
    print(f"Error: {response.exit_code} {response.result}")
else:
    print(f"command  > /home/daytona/volume-dir/test.txt': {response.result}")

response = sandbox1.process.exec("ls -la /home/daytona")
if response.exit_code != 0:
    print(f"Error: {response.exit_code} {response.result}")
else:
    print(f"command 'ls -la /home/daytona': {response.result}")


sandbox2 = daytona.create(
    CreateSandboxParams(volumes=[VolumeMount(volume_id=volume.id, mount_path="/home/daytona/other-volume-dir")])
)
response = sandbox2.process.exec("ls -la /home/daytona")
if response.exit_code != 0:
    print(f"Error: {response.exit_code} {response.result}")
else:
    print(f"command 'ls -la /home/daytona': {response.result}")
response = sandbox2.process.exec("cat /home/daytona/other-volume-dir/test.txt")
if response.exit_code != 0:
    print(f"Error 'cat /home/daytona/other-volume-dir/test.txt': {response.exit_code} {response.result}")
else:
    print(response.result)


daytona.delete(sandbox1)
daytona.delete(sandbox2)
daytona.volume.delete(volume)
