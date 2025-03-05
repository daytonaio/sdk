# Daytona SDK for TypeScript

A TypeScript SDK for interacting with Daytona Server API, providing a simple interface for Daytona Workspace management, Git operations, file system operations, and language server protocol support.

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

// Initialize using environment variables
const daytona = new Daytona()

// Create a workspace
const workspace = await daytona.create()

// Run code in the workspace
const response = await workspace.process.codeRun('console.log("Hello World!")')
console.log(response.result)

// Clean up when done
await daytona.remove(workspace)
```

## Configuration

The SDK can be configured using environment variables or by passing a configuration object:

```typescript
import { Daytona } from '@daytonaio/sdk'

// Initialize with configuration
const daytona = new Daytona({
  apiKey: 'your-api-key',
  serverUrl: 'your-server-url',
  target: 'us',
})
```

Or using environment variables:

- `DAYTONA_API_KEY`: Your Daytona API key
- `DAYTONA_SERVER_URL`: The Daytona server URL
- `DAYTONA_TARGET`: Your target environment

You can also customize workspace creation:

```typescript
const workspace = await daytona.create({
  language: 'typescript',
  envVars: { NODE_ENV: 'development' },
  autoStopInterval: 60, // Auto-stop after 1 hour of inactivity
})
```

## Features

- **Workspace Management**: Create, manage and remove workspaces
- **Git Operations**: Clone repositories, manage branches, and more
- **File System Operations**: Upload, download, search and manipulate files
- **Language Server Protocol**: Interact with language servers for code intelligence
- **Process Management**: Execute code and commands in workspaces

## Examples

### Execute Commands

```typescript
// Execute a shell command
const response = await workspace.process.executeCommand('echo "Hello, World!"')
console.log(response.result)

// Run TypeScript code
const response = await workspace.process.codeRun(`
const x = 10
const y = 20
console.log(\`Sum: \${x + y}\`)
`)
console.log(response.result)
```

### File Operations

```typescript
// Upload a file
await workspace.fs.uploadFile(
  '/path/to/file.txt',
  new File(
    [Buffer.from('Hello, World!')],
    'file.txt',
    { type: 'text/plain' }
  )
)

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
