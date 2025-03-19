import os
from daytona_sdk import Daytona, CreateWorkspaceParams, DaytonaConfig

config = DaytonaConfig(
    api_key="dtn_0d522da04d7e07c4da8693edce78b43d58b20822bf6a98eb478615065aa445ac",
    server_url="https://stage.daytona.work/api",
    target="eu"
)

daytona = Daytona(config)
params = CreateWorkspaceParams(
  language="python",
)

# First, create a sandbox
sandbox = daytona.create(params)

# Get sandbox root directory
root_dir = sandbox.get_user_root_dir()

# List files in the sandbox
files = sandbox.fs.list_files(root_dir)
print("Files:", files)

# Create a new directory in the sandbox
new_dir = os.path.join(root_dir, "new-dir")
sandbox.fs.create_folder(new_dir, "755")

file_path = os.path.join(new_dir, "data.txt")

# Add a new file to the sandbox
file_content = b"Hello, World!"
sandbox.fs.upload_file(file_path, file_content)

# Search for the file we just added
matches = sandbox.fs.find_files(root_dir, "World!")
print("Matches:", matches)

# Replace the contents of the file
sandbox.fs.replace_in_files([file_path], "Hello, World!", "Goodbye, World!")

# Read the file
downloaded_file = sandbox.fs.download_file(file_path)
print("File content:", downloaded_file.decode("utf-8"))

# Change the file permissions
sandbox.fs.set_file_permissions(file_path, mode="777")

# Get file info
file_info = sandbox.fs.get_file_info(file_path)
print("File info:", file_info)  # Should show the new permissions

# Move the file to the new location
new_file_path = os.path.join(root_dir, "moved-data.txt")
sandbox.fs.move_files(file_path, new_file_path)

# Find the file in the new location
search_results = sandbox.fs.search_files(root_dir, "moved-data.txt")
print("Search results:", search_results)

# Delete the file
sandbox.fs.delete_file(new_file_path)

daytona.remove(sandbox)
