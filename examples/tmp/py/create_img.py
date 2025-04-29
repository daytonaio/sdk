from daytona_sdk import Daytona, Image

daytona = Daytona()

image = (
    Image.base("python:3.13.2-slim-bookworm")
    .run_commands("pip install uuid")
    .add_local_dir("/workspaces/sdk/docs", "/home/daytona/sdk-docs")
)

daytona.create_image("test-image:0.0.21", image, verbose=True)
