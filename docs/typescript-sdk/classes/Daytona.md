[Daytona TypeScript SDK - v0.1.3](../README.md) / Daytona

# Class: Daytona

Main class for interacting with Daytona Server API
 Daytona

## Table of contents

### Constructors

- [constructor](Daytona.md#constructor)

### Methods

- [create](Daytona.md#create)
- [remove](Daytona.md#remove)

## Constructors

### constructor

• **new Daytona**(`config?`): [`Daytona`](Daytona.md)

Creates a new Daytona client instance

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `config?` | [`DaytonaConfig`](../interfaces/DaytonaConfig.md) | Configuration options |

#### Returns

[`Daytona`](Daytona.md)

**`Throws`**

When API key or server URL is missing

#### Defined in

[Daytona.ts:64](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Daytona.ts#L64)

## Methods

### create

▸ **create**(`params?`): `Promise`\<[`Workspace`](Workspace.md)\>

Creates a new workspace

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `params?` | [`CreateWorkspaceParams`](../interfaces/CreateWorkspaceParams.md) | Parameters for workspace creation |

#### Returns

`Promise`\<[`Workspace`](Workspace.md)\>

The created workspace instance

#### Defined in

[Daytona.ts:97](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Daytona.ts#L97)

___

### remove

▸ **remove**(`workspace`): `Promise`\<`void`\>

Removes a workspace

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `workspace` | [`Workspace`](Workspace.md) | The workspace to remove |

#### Returns

`Promise`\<`void`\>

#### Defined in

[Daytona.ts:165](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Daytona.ts#L165)
