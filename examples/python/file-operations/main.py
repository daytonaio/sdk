import os

from daytona_sdk import CreateSandboxParams, Daytona

daytona = Daytona()
params = CreateSandboxParams(
    language="python",
)

# First, create a sandbox
sandbox = daytona.create(params)

# List files in the sandbox
files = sandbox.fs.list_files("~")
print("Files:", files)

# Create a new directory in the sandbox
new_dir = "new-dir"
sandbox.fs.create_folder(new_dir, "755")

file_path = os.path.join(new_dir, "data.txt")

# Add a new file to the sandbox
file_content = b"Hello, World!"
sandbox.fs.upload_file(file_path, file_content)

# Search for the file we just added
matches = sandbox.fs.find_files("~", "World!")
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
new_file_path = "moved-data.txt"
sandbox.fs.move_files(file_path, new_file_path)

# Find the file in the new location
search_results = sandbox.fs.search_files("~", "moved-data.txt")
print("Search results:", search_results)

# Delete the file
sandbox.fs.delete_file(new_file_path)

daytona.delete(sandbox)
