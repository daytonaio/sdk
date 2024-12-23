[Daytona TypeScript SDK - v0.1.3](../README.md) / CreateWorkspaceParams

# Interface: CreateWorkspaceParams

Parameters for creating a new workspace
 CreateWorkspaceParams

## Table of contents

### Properties

- [id](CreateWorkspaceParams.md#id)
- [image](CreateWorkspaceParams.md#image)
- [language](CreateWorkspaceParams.md#language)

## Properties

### id

• `Optional` **id**: `string`

Optional workspace ID. If not provided, a random ID will be generated

#### Defined in

[Daytona.ts:39](https://github.com/daytonaio/sdk/blob/626c9044a00981097946c265eb07e895370c02bc/packages/typescript/src/Daytona.ts#L39)

___

### image

• `Optional` **image**: `string`

Optional Docker image to use for the workspace

#### Defined in

[Daytona.ts:41](https://github.com/daytonaio/sdk/blob/626c9044a00981097946c265eb07e895370c02bc/packages/typescript/src/Daytona.ts#L41)

___

### language

• **language**: `CodeLanguage`

Programming language to use in the workspace

#### Defined in

[Daytona.ts:43](https://github.com/daytonaio/sdk/blob/626c9044a00981097946c265eb07e895370c02bc/packages/typescript/src/Daytona.ts#L43)
