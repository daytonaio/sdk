from daytona_sdk import Daytona, Image

daytona = Daytona()

image = Image.base("python:3.13.2-slim-bookworm").run_commands("pip install uuid matplotlib seaborn numpy scipy")

print("Creating image...")
daytona.create_image("id-test-image:0.0.69", image, on_logs=print)
print("Image created")
