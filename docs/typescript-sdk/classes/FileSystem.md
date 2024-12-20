[Daytona TypeScript SDK - v0.1.3](../README.md) / FileSystem

# Class: FileSystem

Provides file system operations within a workspace
 FileSystem

## Table of contents

### Constructors

- [constructor](FileSystem.md#constructor)

### Methods

- [createFolder](FileSystem.md#createfolder)
- [deleteFile](FileSystem.md#deletefile)
- [downloadFile](FileSystem.md#downloadfile)
- [findFiles](FileSystem.md#findfiles)
- [getFileDetails](FileSystem.md#getfiledetails)
- [listFiles](FileSystem.md#listfiles)
- [moveFiles](FileSystem.md#movefiles)
- [replaceInFiles](FileSystem.md#replaceinfiles)
- [searchFiles](FileSystem.md#searchfiles)
- [setFilePermissions](FileSystem.md#setfilepermissions)
- [uploadFile](FileSystem.md#uploadfile)

## Constructors

### constructor

• **new FileSystem**(`instance`, `toolboxApi`): [`FileSystem`](FileSystem.md)

#### Parameters

| Name | Type |
| :------ | :------ |
| `instance` | `Workspace` |
| `toolboxApi` | `WorkspaceToolboxApi` |

#### Returns

[`FileSystem`](FileSystem.md)

#### Defined in

[FileSystem.ts:29](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/FileSystem.ts#L29)

## Methods

### createFolder

▸ **createFolder**(`path`, `mode`): `Promise`\<`void`\>

Creates a new folder in the workspace

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Path where the folder should be created |
| `mode` | `string` | Folder permissions in octal format |

#### Returns

`Promise`\<`void`\>

#### Defined in

[FileSystem.ts:40](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/FileSystem.ts#L40)

___

### deleteFile

▸ **deleteFile**(`path`): `Promise`\<`void`\>

Deletes a file from the workspace

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Path to the file to delete |

#### Returns

`Promise`\<`void`\>

#### Defined in

[FileSystem.ts:54](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/FileSystem.ts#L54)

___

### downloadFile

▸ **downloadFile**(`path`): `Promise`\<`Blob`\>

Downloads a file from the workspace

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Path to the file to download |

#### Returns

`Promise`\<`Blob`\>

The file contents as a Blob

#### Defined in

[FileSystem.ts:67](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/FileSystem.ts#L67)

___

### findFiles

▸ **findFiles**(`path`, `pattern`): `Promise`\<[`Match`](../interfaces/Match.md)[]\>

Searches for files matching a pattern

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Directory to search in |
| `pattern` | `string` | Search pattern |

#### Returns

`Promise`\<[`Match`](../interfaces/Match.md)[]\>

Array of matching files

#### Defined in

[FileSystem.ts:81](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/FileSystem.ts#L81)

___

### getFileDetails

▸ **getFileDetails**(`path`): `Promise`\<[`FileInfo`](../interfaces/FileInfo.md)\>

Gets details about a file

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Path to the file |

#### Returns

`Promise`\<[`FileInfo`](../interfaces/FileInfo.md)\>

File information

#### Defined in

[FileSystem.ts:95](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/FileSystem.ts#L95)

___

### listFiles

▸ **listFiles**(`path`): `Promise`\<[`FileInfo`](../interfaces/FileInfo.md)[]\>

Lists files in a directory

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Directory path to list |

#### Returns

`Promise`\<[`FileInfo`](../interfaces/FileInfo.md)[]\>

Array of file information

#### Defined in

[FileSystem.ts:108](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/FileSystem.ts#L108)

___

### moveFiles

▸ **moveFiles**(`source`, `destination`): `Promise`\<`void`\>

Moves/renames files

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `source` | `string` | Source path |
| `destination` | `string` | Destination path |

#### Returns

`Promise`\<`void`\>

#### Defined in

[FileSystem.ts:122](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/FileSystem.ts#L122)

___

### replaceInFiles

▸ **replaceInFiles**(`files`, `pattern`, `newValue`): `Promise`\<[`ReplaceResult`](../interfaces/ReplaceResult.md)[]\>

Replaces text in multiple files

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `files` | `string`[] | Array of file paths |
| `pattern` | `string` | Pattern to replace |
| `newValue` | `string` | Replacement value |

#### Returns

`Promise`\<[`ReplaceResult`](../interfaces/ReplaceResult.md)[]\>

Results of the replace operation

#### Defined in

[FileSystem.ts:138](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/FileSystem.ts#L138)

___

### searchFiles

▸ **searchFiles**(`path`, `pattern`): `Promise`\<[`SearchFilesResponse`](../interfaces/SearchFilesResponse.md)\>

Searches for files by name pattern

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Directory to search in |
| `pattern` | `string` | Search pattern |

#### Returns

`Promise`\<[`SearchFilesResponse`](../interfaces/SearchFilesResponse.md)\>

Search results

#### Defined in

[FileSystem.ts:162](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/FileSystem.ts#L162)

___

### setFilePermissions

▸ **setFilePermissions**(`path`, `permissions`): `Promise`\<`void`\>

Sets file permissions

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Path to the file |
| `permissions` | `FilePermissionsParams` | Permission settings |

#### Returns

`Promise`\<`void`\>

#### Defined in

[FileSystem.ts:180](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/FileSystem.ts#L180)

___

### uploadFile

▸ **uploadFile**(`path`, `file`): `Promise`\<`void`\>

Uploads a file to the workspace

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Destination path |
| `file` | `Blob` | File contents to upload |

#### Returns

`Promise`\<`void`\>

#### Defined in

[FileSystem.ts:200](https://github.com/daytonaio/sdk/blob/b45168f061cd6be86cb18d4f6da11d28c59292bf/packages/typescript/src/FileSystem.ts#L200)
