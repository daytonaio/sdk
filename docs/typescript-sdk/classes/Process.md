[Daytona TypeScript SDK - v0.1.3](../README.md) / Process

# Class: Process

Handles process and code execution within a workspace
 Process

## Table of contents

### Constructors

- [constructor](Process.md#constructor)

### Methods

- [codeRun](Process.md#coderun)
- [processExecuteCommand](Process.md#processexecutecommand)

## Constructors

### constructor

• **new Process**(`codeToolbox`, `toolboxApi`, `instance`): [`Process`](Process.md)

#### Parameters

| Name | Type |
| :------ | :------ |
| `codeToolbox` | [`WorkspaceCodeToolbox`](../interfaces/WorkspaceCodeToolbox.md) |
| `toolboxApi` | `WorkspaceToolboxApi` |
| `instance` | `Workspace` |

#### Returns

[`Process`](Process.md)

#### Defined in

[Process.ts:13](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Process.ts#L13)

## Methods

### codeRun

▸ **codeRun**(`code`): `Promise`\<[`ExecuteResponse`](../interfaces/ExecuteResponse.md)\>

Executes code in the workspace using the appropriate language runtime

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `code` | `string` | Code to execute |

#### Returns

`Promise`\<[`ExecuteResponse`](../interfaces/ExecuteResponse.md)\>

Code execution results

#### Defined in

[Process.ts:41](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Process.ts#L41)

___

### processExecuteCommand

▸ **processExecuteCommand**(`command`): `Promise`\<[`ExecuteResponse`](../interfaces/ExecuteResponse.md)\>

Executes a shell command in the workspace

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `command` | `string` | Command to execute |

#### Returns

`Promise`\<[`ExecuteResponse`](../interfaces/ExecuteResponse.md)\>

Command execution results

#### Defined in

[Process.ts:24](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Process.ts#L24)
