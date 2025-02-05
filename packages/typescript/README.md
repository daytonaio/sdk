# Daytona SDK for TypeScript

A TypeScript SDK for interacting with Daytona Server API, providing a simple interface for Daytona Workspace management, Git operations, file system operations, and language server protocol support.

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

You can install the package using npm:

```bash
npm install @daytonaio/sdk
```

Or using yarn:

```bash
yarn add @daytonaio/sdk
```

## Quick Start

Here's a simple example of using the SDK:

```typescript
import { Daytona } from '@daytonaio/sdk'

// Initialize the Daytona client
const daytona = new Daytona()

// Create the workspace instance
const workspace = await daytona.create({
  language: 'typescript',
})

// Run the code securely inside the workspace
const response = await workspace.process.code_run('console.log("Hello World!")')
console.log(response.result)
```

## Features

- **Workspace Management**: Create, manage and remove workspaces
- **Git Operations**: Clone repositories, manage branches, and more
- **File System Operations**: Upload, download, search and manipulate files
- **Language Server Protocol**: Interact with language servers for code intelligence
- **Process Management**: Execute code and commands in workspaces

## Configuration

The SDK can be configured using environment variables or by passing a configuration object:

```typescript
import { Daytona, DaytonaConfig } from '@daytonaio/sdk'

const config: DaytonaConfig = {
  apiKey: 'your-api-key',
  serverUrl: 'https://your-daytona-server',
  target: 'your-target',
}

const daytona = new Daytona(config)
```

Or using environment variables:

- `DAYTONA_API_KEY`: Your Daytona API key
- `DAYTONA_SERVER_URL`: The Daytona server URL
- `DAYTONA_TARGET`: Your target environment

## Examples

### Execute command

```typescript
const response = await workspace.process.code_run(
  'print("Sum of 3 and 4 is " + str(3 + 4))',
)
if (response.code !== 0) {
  console.log(`Error: ${response.code} ${response.result}`)
} else {
  console.log(response.result)
}
```

### File Operations

```typescript
// Upload a file
await workspace.fs.uploadFile('/path/to/file.txt', new Blob(['Hello, World!']))

// Download a file
const content = await workspace.fs.downloadFile('/path/to/file.txt')

// Search for files
const matches = await workspace.fs.findFiles(root_dir, 'search_pattern')
```

### Git Operations

```typescript
// Clone a repository
await workspace.git.clone('https://github.com/example/repo', '/path/to/clone')

// List branches
const branches = await workspace.git.branches('/path/to/repo')

// Add files
await workspace.git.add('/path/to/repo', ['file1.txt', 'file2.txt'])
```

### Language Server Protocol

```typescript
// Create and start a language server
const lsp = workspace.createLspServer('typescript', '/path/to/project')
await lsp.start()

// Notify the lsp for the file
await lsp.didOpen('/path/to/file.ts')

// Get document symbols
const symbols = await lsp.documentSymbols('/path/to/file.ts')

// Get completions
const completions = await lsp.completions('/path/to/file.ts', {
  line: 10,
  character: 15,
})
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
