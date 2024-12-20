[Daytona TypeScript SDK - v0.1.3](../README.md) / Git

# Class: Git

Provides Git operations within a workspace
 Git

## Table of contents

### Constructors

- [constructor](Git.md#constructor)

### Methods

- [add](Git.md#add)
- [branches](Git.md#branches)
- [clone](Git.md#clone)
- [commit](Git.md#commit)
- [pull](Git.md#pull)
- [push](Git.md#push)
- [status](Git.md#status)

## Constructors

### constructor

• **new Git**(`workspace`, `toolboxApi`, `instance`): [`Git`](Git.md)

#### Parameters

| Name | Type |
| :------ | :------ |
| `workspace` | [`Workspace`](Workspace.md) |
| `toolboxApi` | `WorkspaceToolboxApi` |
| `instance` | `Workspace` |

#### Returns

[`Git`](Git.md)

#### Defined in

[Git.ts:15](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Git.ts#L15)

## Methods

### add

▸ **add**(`path`, `files`): `Promise`\<`void`\>

Stages files for commit

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Repository path |
| `files` | `string`[] | Array of file paths to stage |

#### Returns

`Promise`\<`void`\>

#### Defined in

[Git.ts:27](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Git.ts#L27)

___

### branches

▸ **branches**(`path`): `Promise`\<[`ListBranchResponse`](../interfaces/ListBranchResponse.md)\>

Lists branches in the repository

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Repository path |

#### Returns

`Promise`\<[`ListBranchResponse`](../interfaces/ListBranchResponse.md)\>

List of branches

#### Defined in

[Git.ts:43](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Git.ts#L43)

___

### clone

▸ **clone**(`url`, `path`, `branch?`, `commitId?`, `username?`, `password?`): `Promise`\<`void`\>

Clones a Git repository

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `url` | `string` | Repository URL |
| `path` | `string` | Destination path |
| `branch?` | `string` | Branch to clone |
| `commitId?` | `string` | Specific commit to clone |
| `username?` | `string` | Git username for authentication |
| `password?` | `string` | Git password/token for authentication |

#### Returns

`Promise`\<`void`\>

#### Defined in

[Git.ts:61](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Git.ts#L61)

___

### commit

▸ **commit**(`path`, `message`, `author`, `email`): `Promise`\<`void`\>

Creates a new commit with staged changes

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Repository path |
| `message` | `string` | Commit message |
| `author` | `string` | Author name |
| `email` | `string` | Author email |

#### Returns

`Promise`\<`void`\>

#### Defined in

[Git.ts:91](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Git.ts#L91)

___

### pull

▸ **pull**(`path`, `username?`, `password?`): `Promise`\<`void`\>

Pulls changes from remote repository

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Repository path |
| `username?` | `string` | Git username for authentication |
| `password?` | `string` | Git password/token for authentication |

#### Returns

`Promise`\<`void`\>

#### Defined in

[Git.ts:139](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Git.ts#L139)

___

### push

▸ **push**(`path`, `username?`, `password?`): `Promise`\<`void`\>

Pushes local commits to remote repository

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Repository path |
| `username?` | `string` | Git username for authentication |
| `password?` | `string` | Git password/token for authentication |

#### Returns

`Promise`\<`void`\>

#### Defined in

[Git.ts:116](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Git.ts#L116)

___

### status

▸ **status**(`path`): `Promise`\<[`GitStatus`](../interfaces/GitStatus.md)\>

Gets the current Git repository status

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Repository path |

#### Returns

`Promise`\<[`GitStatus`](../interfaces/GitStatus.md)\>

Repository status information

#### Defined in

[Git.ts:160](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/Git.ts#L160)
