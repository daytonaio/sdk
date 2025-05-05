# Daytona SDK for Python

A Python SDK for interacting with the Daytona API, providing a simple interface for Daytona Sandbox management, Git operations, file system operations, and language server protocol support.

## Installation

You can install the package using pip:

```bash
pip install daytona-sdk
```

## Quick Start

Here's a simple example of using the SDK:

```python
from daytona_sdk import Daytona

# Initialize using environment variables
daytona = Daytona()

# Create a sandbox
sandbox = daytona.create()

# Run code in the sandbox
response = sandbox.process.code_run('print("Hello World!")')
print(response.result)

# Clean up when done
daytona.delete(sandbox)
```

## Configuration

The SDK can be configured using environment variables or by passing a configuration object:

```python
from daytona_sdk import Daytona, DaytonaConfig

# Initialize with configuration
config = DaytonaConfig(
    api_key="your-api-key",
    api_url="your-api-url",
    target="us"
)
daytona = Daytona(config)
```

Or using environment variables:

- `DAYTONA_API_KEY`: Your Daytona API key
- `DAYTONA_API_URL`: The Daytona API URL
- `DAYTONA_TARGET`: Your target environment

You can also customize sandbox creation:

```python
sandbox = daytona.create(CreateSandboxParams(
    language="python",
    env_vars={"PYTHON_ENV": "development"},
    auto_stop_interval=60  # Auto-stop after 1 hour of inactivity
))
```

## Features

- **Sandbox Management**: Create, manage and remove sandboxes
- **Git Operations**: Clone repositories, manage branches, and more
- **File System Operations**: Upload, download, search and manipulate files
- **Language Server Protocol**: Interact with language servers for code intelligence
- **Process Management**: Execute code and commands in sandboxes

## Examples

### Execute Commands

```python
# Execute a shell command
response = sandbox.process.exec('echo "Hello, World!"')
print(response.result)

# Run Python code
response = sandbox.process.code_run('''
x = 10
y = 20
print(f"Sum: {x + y}")
''')
print(response.result)
```

### File Operations

```python
# Upload a file
sandbox.fs.upload_file('path/to/file.txt', b'Hello, World!')

# Download a file
content = sandbox.fs.download_file('path/to/file.txt')

# Search for files
matches = sandbox.fs.find_files(root_dir, 'search_pattern')
```

### Git Operations

```python
# Clone a repository
sandbox.git.clone('https://github.com/example/repo', 'path/to/clone')

# List branches
branches = sandbox.git.branches('path/to/repo')

# Add files
sandbox.git.add('path/to/repo', ['file1.txt', 'file2.txt'])
```

### Language Server Protocol

```python
# Create and start a language server
lsp = sandbox.create_lsp_server('typescript', 'path/to/project')
lsp.start()

# Notify the lsp for the file
lsp.did_open('path/to/file.ts')

# Get document symbols
symbols = lsp.document_symbols('path/to/file.ts')

# Get completions
completions = lsp.completions('path/to/file.ts', {"line": 10, "character": 15})
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
