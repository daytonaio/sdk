[Daytona TypeScript SDK - v0.1.3](../README.md) / LspServer

# Class: LspServer

Provides Language Server Protocol (LSP) functionality
 LspServer

## Table of contents

### Constructors

- [constructor](LspServer.md#constructor)

### Methods

- [completions](LspServer.md#completions)
- [didClose](LspServer.md#didclose)
- [didOpen](LspServer.md#didopen)
- [documentSymbols](LspServer.md#documentsymbols)
- [start](LspServer.md#start)
- [stop](LspServer.md#stop)
- [workspaceSymbols](LspServer.md#workspacesymbols)

## Constructors

### constructor

• **new LspServer**(`languageId`, `pathToProject`, `toolboxApi`, `instance`): [`LspServer`](LspServer.md)

#### Parameters

| Name | Type |
| :------ | :------ |
| `languageId` | ``"typescript"`` |
| `pathToProject` | `string` |
| `toolboxApi` | `WorkspaceToolboxApi` |
| `instance` | `Workspace` |

#### Returns

[`LspServer`](LspServer.md)

#### Defined in

[LspServer.ts:30](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/LspServer.ts#L30)

## Methods

### completions

▸ **completions**(`path`, `position`): `Promise`\<[`CompletionList`](../interfaces/CompletionList.md)\>

Gets code completion suggestions

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Path to the file |
| `position` | [`Position`](../interfaces/Position.md) | Cursor position |

#### Returns

`Promise`\<[`CompletionList`](../interfaces/CompletionList.md)\>

List of completion suggestions

#### Defined in

[LspServer.ts:137](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/LspServer.ts#L137)

___

### didClose

▸ **didClose**(`path`): `Promise`\<`void`\>

Notifies the server that a file has been closed

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Path to the closed file |

#### Returns

`Promise`\<`void`\>

#### Defined in

[LspServer.ts:89](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/LspServer.ts#L89)

___

### didOpen

▸ **didOpen**(`path`): `Promise`\<`void`\>

Notifies the server that a file has been opened

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Path to the opened file |

#### Returns

`Promise`\<`void`\>

#### Defined in

[LspServer.ts:72](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/LspServer.ts#L72)

___

### documentSymbols

▸ **documentSymbols**(`path`): `Promise`\<[`LspSymbol`](../interfaces/LspSymbol.md)[]\>

Gets document symbols (functions, classes, etc.)

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Path to the file |

#### Returns

`Promise`\<[`LspSymbol`](../interfaces/LspSymbol.md)[]\>

Array of document symbols

#### Defined in

[LspServer.ts:106](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/LspServer.ts#L106)

___

### start

▸ **start**(): `Promise`\<`void`\>

Starts the language server

#### Returns

`Promise`\<`void`\>

#### Defined in

[LspServer.ts:41](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/LspServer.ts#L41)

___

### stop

▸ **stop**(): `Promise`\<`void`\>

Stops the language server

#### Returns

`Promise`\<`void`\>

#### Defined in

[LspServer.ts:56](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/LspServer.ts#L56)

___

### workspaceSymbols

▸ **workspaceSymbols**(`query`): `Promise`\<[`LspSymbol`](../interfaces/LspSymbol.md)[]\>

Searches for symbols across the workspace

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `query` | `string` | Search query |

#### Returns

`Promise`\<[`LspSymbol`](../interfaces/LspSymbol.md)[]\>

Array of matching symbols

#### Defined in

[LspServer.ts:121](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/LspServer.ts#L121)
