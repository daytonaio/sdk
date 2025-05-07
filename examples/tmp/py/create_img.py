from daytona_sdk import Daytona, Image

daytona = Daytona()

image = Image.base("python:3.13.2-slim-bookworm").run_commands("pip install uuid black")

print("Creating image...")
daytona.create_image("test-image:0.0.24", image, on_logs=print)
print("Image created")
