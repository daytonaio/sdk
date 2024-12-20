# Daytona SDK for Python

A Python SDK for interacting with Daytona Server API, providing a simple interface for Daytona Workspace management, Git operations, file system operations, and language server protocol support.

## Prerequisites

Before using the Daytona SDK, you need to have a running Daytona server instance and proper configuration.

### Server Installation

For detailed instructions on installing and setting up the Daytona server, please refer to the official installation guide at:
[https://github.com/daytonaio/daytona](https://github.com/daytonaio/daytona)

### Configuration

To use the SDK, you'll need two essential pieces of information:

1. **Server Address**:

   - Run `daytona server config` to get your server's configuration
   - Look for the `API URL` value in the output
   - For testing and development, you can use the FRP address provided
   - For production environments, it's recommended to use a static address

2. **API Key**:
   - Generate a new API key by running:
     ```bash
     daytona api-key generate
     ```
   - Save this key securely as it will be needed to authenticate with the server

## Installation

You can install the package using pip:

```bash
pip install daytona-sdk
```

## Quick Start

Here's a simple example of using the SDK:

```python
from daytona_sdk import Daytona

# Initialize the Daytona client
daytona = Daytona()

# Create the workspace instance
workspace = daytona.create()

# Run the code securely inside the workspace
response = workspace.process.code_run('print("Hello World!")')
print(response.result)
```

## Features

- **Workspace Management**: Create, manage and remove workspaces
- **Git Operations**: Clone repositories, manage branches, and more
- **File System Operations**: Upload, download, search and manipulate files
- **Language Server Protocol**: Interact with language servers for code intelligence
- **Process Management**: Execute code and commands in workspaces

## Configuration

The SDK can be configured using environment variables or by passing a configuration object:

```python
from daytona_sdk import Daytona, DaytonaConfig

config = DaytonaConfig(
    api_key='your-api-key',
    server_url='https://your-daytona-server',
    target='your-target'
)

daytona = Daytona(config)
```

Or using environment variables:

- `DAYTONA_API_KEY`: Your Daytona API key
- `DAYTONA_SERVER_URL`: The Daytona server URL
- `DAYTONA_TARGET`: Your target environment

## Examples

### Execute command

```python
response = workspace.process.code_run('print("Sum of 3 and 4 is " + str(3 + 4))')
if response.code != 0:
    print(f"Error: {response.code} {response.result}")
else:
    print(response.result)
```

### File Operations

```python
# Upload a file
workspace.fs.upload_file('/path/to/file.txt', b'Hello, World!')

# Download a file
content = workspace.fs.download_file('/path/to/file.txt')

# Search for files
matches = workspace.fs.find_files(root_dir, 'search_pattern')
```

### Git Operations

```python
# Clone a repository
workspace.git.clone('https://github.com/example/repo', '/path/to/clone')

# List branches
branches = workspace.git.branches('/path/to/repo')

# Add files
workspace.git.add('/path/to/repo', ['file1.txt', 'file2.txt'])
```

### Language Server Protocol

```python
# Create and start a language server
lsp = workspace.create_lsp_server('typescript', '/path/to/project')
lsp.start()

# Notify the lsp for the file
lsp.did_open('/path/to/file.ts')

# Get document symbols
symbols = lsp.document_symbols('/path/to/file.ts')

# Get completions
completions = lsp.completions('/path/to/file.ts', {"line": 10, "character": 15})
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License, Version 2.0 - see below for details:

```
Copyright 2024 Daytona

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

For the full license text, please see the [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0).