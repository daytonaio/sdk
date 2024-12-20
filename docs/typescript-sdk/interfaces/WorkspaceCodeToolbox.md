[Daytona TypeScript SDK - v0.1.3](../README.md) / WorkspaceCodeToolbox

# Interface: WorkspaceCodeToolbox

Interface defining methods that a code toolbox must implement
 WorkspaceCodeToolbox

## Table of contents

### Methods

- [getDefaultImage](WorkspaceCodeToolbox.md#getdefaultimage)
- [getRunCommand](WorkspaceCodeToolbox.md#getruncommand)

## Methods

### getDefaultImage

▸ **getDefaultImage**(): `string`

Gets the default Docker image for this language

#### Returns

`string`

#### Defined in

[Workspace.ts:13](https://github.com/daytonaio/sdk/blob/626c9044a00981097946c265eb07e895370c02bc/packages/typescript/src/Workspace.ts#L13)

___

### getRunCommand

▸ **getRunCommand**(`code`): `string`

Generates a command to run the provided code

#### Parameters

| Name | Type |
| :------ | :------ |
| `code` | `string` |

#### Returns

`string`

#### Defined in

[Workspace.ts:15](https://github.com/daytonaio/sdk/blob/626c9044a00981097946c265eb07e895370c02bc/packages/typescript/src/Workspace.ts#L15)
