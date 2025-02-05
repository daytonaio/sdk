# Daytona SDK

Official Python and TypeScript SDKs for interacting with Daytona, providing simple interfaces for managing development environments programmatically. This repository contains both SDK libraries, offering native integration options for Python and TypeScript/JavaScript applications.

## SDK Examples

### TypeScript/JavaScript

Install the SDK:

```bash
npm install @daytonaio/sdk
# or
yarn add @daytonaio/sdk
```

Basic usage:

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

### Python

Install the SDK:

```bash
pip install daytona-sdk
```

Basic usage:

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

## About Daytona

Daytona is a radically simple open source development environment manager that allows developers to spin up fully configured development environments with a single command. It eliminates the complexity of setting up development environments, whether they're local, remote, cloud-based, or on physical servers, supporting both x86 and ARM architectures.

While Daytona offers a straightforward way to manage development environments, these SDKs bring that same power to your Python and TypeScript applications, enabling programmatic control over your development infrastructure.

## Why Daytona SDK?

These SDKs extend Daytona's capabilities by allowing you to:

- Integrate Daytona's functionality into your existing Python and TypeScript applications
- Automate development environment creation and management
- Programmatically handle workspace configurations
- Manage Git operations and repository connections
- Control file system operations within workspaces
- Interface with language server protocols
- Build custom tooling and automation around your development environments
- Create isolated environments for running AI-generated code safely
- Set up data processing pipelines with configurable compute resources
- Deploy and test machine learning models in isolated environments

## AI and Data Processing Use Cases

Daytona SDKs excel in scenarios involving AI and data processing, offering flexible deployment options across multiple infrastructure providers and technologies:

- **AI Code Execution**: Create isolated environments to safely run and test AI-generated code on your choice of infrastructure:

  - Deploy identical environments across AWS, GCP, Azure, or any major cloud provider
  - Leverage Kubernetes clusters for scalability
  - Quickly create ephemeral environments for parallel code generation trajectories

- **Data Processing Pipelines**: Configure and manage environments for data processing workflows:

  - Choose optimal infrastructure based on data locality
  - Enable distributed processing
  - Scale across multiple cloud regions
  - Support hybrid cloud deployments

- **Resource Management**: Dynamically allocate compute resources based on workload requirements:

  - Provision resources across different cloud providers
  - Scale container resources on demand
  - Manage Kubernetes cluster resources
  - Support bare metal resource allocation

- **Environment Isolation**: Ensure security when running untrusted code or processing sensitive data:
  - Configurable isolation level: Sysbox, LVMs, VMs
  - Provision dedicated VMs for enhanced isolation
  - Deploy in private cloud environments
  - Utilize network isolation features
  - Implement cloud-specific security controls

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
