[Daytona TypeScript SDK - v0.1.3](../README.md) / Workspace

# Class: Workspace

Represents a Daytona workspace instance with file system, git, and process management capabilities
 Workspace

## Table of contents

### Constructors

- [constructor](Workspace.md#constructor)

### Properties

- [fs](Workspace.md#fs)
- [git](Workspace.md#git)
- [id](Workspace.md#id)
- [process](Workspace.md#process)
- [toolboxApi](Workspace.md#toolboxapi)

### Methods

- [createLspServer](Workspace.md#createlspserver)
- [getWorkspaceRootDir](Workspace.md#getworkspacerootdir)

## Constructors

### constructor

• **new Workspace**(`id`, `instance`, `toolboxApi`, `codeToolbox`): [`Workspace`](Workspace.md)

Creates a new workspace instance

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `id` | `string` | Unique identifier for the workspace |
| `instance` | `Workspace` | The underlying workspace instance |
| `toolboxApi` | `WorkspaceToolboxApi` | API client for workspace operations |
| `codeToolbox` | [`WorkspaceCodeToolbox`](../interfaces/WorkspaceCodeToolbox.md) | Language-specific toolbox implementation |

#### Returns

[`Workspace`](Workspace.md)

#### Defined in

[Workspace.ts:37](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Workspace.ts#L37)

## Properties

### fs

• `Readonly` **fs**: [`FileSystem`](FileSystem.md)

File system operations for the workspace

#### Defined in

[Workspace.ts:24](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Workspace.ts#L24)

___

### git

• `Readonly` **git**: [`Git`](Git.md)

Git operations for the workspace

#### Defined in

[Workspace.ts:26](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Workspace.ts#L26)

___

### id

• `Readonly` **id**: `string`

Unique identifier for the workspace

#### Defined in

[Workspace.ts:38](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Workspace.ts#L38)

___

### process

• `Readonly` **process**: [`Process`](Process.md)

Process and code execution operations

#### Defined in

[Workspace.ts:28](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Workspace.ts#L28)

___

### toolboxApi

• `Readonly` **toolboxApi**: `WorkspaceToolboxApi`

API client for workspace operations

#### Defined in

[Workspace.ts:40](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Workspace.ts#L40)

## Methods

### createLspServer

▸ **createLspServer**(`languageId`, `pathToProject`): [`LspServer`](LspServer.md)

Creates a new Language Server Protocol (LSP) server instance

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `languageId` | ``"typescript"`` | The language server type |
| `pathToProject` | `string` | Path to the project root |

#### Returns

[`LspServer`](LspServer.md)

A new LSP server instance

#### Defined in

[Workspace.ts:66](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Workspace.ts#L66)

___

### getWorkspaceRootDir

▸ **getWorkspaceRootDir**(): `Promise`\<`string`\>

Gets the root directory path of the workspace

#### Returns

`Promise`\<`string`\>

The absolute path to the workspace root

#### Defined in

[Workspace.ts:52](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Workspace.ts#L52)
