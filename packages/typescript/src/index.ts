export { Daytona } from './Daytona'
export type { DaytonaConfig, CreateSandboxParams, SandboxResources } from './Daytona'
export { CodeLanguage } from './Daytona'
export { FileSystem } from './FileSystem'
export { Git } from './Git'
export { Process } from './Process'
export { LspLanguageId } from './LspServer'
// export { LspServer } from './LspServer'
// export type { LspLanguageId, Position } from './LspServer'
export { DaytonaError } from './errors/DaytonaError'
export { Sandbox } from './Sandbox'
export type { SandboxCodeToolbox } from './Sandbox'

// Chart and artifact types
export { ChartType } from './types/Chart'
export type { Chart } from './types/Chart'

export type { ExecutionArtifacts, ExecuteResponse as EnhancedExecuteResponse } from './types/ExecuteResponse'

// Re-export necessary types from client
export type {
  FileInfo,
  Match,
  ReplaceResult,
  SearchFilesResponse,
  GitStatus,
  ListBranchResponse,
} from '@daytonaio/api-client'
export { WorkspaceState as SandboxState, CreateWorkspaceTargetEnum as SandboxTargetRegion } from '@daytonaio/api-client'

// Re-export necessary Workspace-related types for backward compatibility
import { WorkspaceState as WS, CreateWorkspaceTargetEnum } from '@daytonaio/api-client'
import { Sandbox } from './Sandbox'
import type { SandboxCodeToolbox } from './Sandbox'
import type { CreateSandboxParams, SandboxResources } from './Daytona'

/** @deprecated `CreateWorkspaceParams` is deprecated. Please use `CreateSandboxParams` instead. This will be removed in a future version. */
export type CreateWorkspaceParams = CreateSandboxParams

/** @deprecated `Workspace` is deprecated. Please use `Sandbox` instead. This will be removed in a future version. */
export const Workspace = Sandbox
/** @deprecated `Workspace` is deprecated. Please use `Sandbox` instead. This will be removed in a future version. */
export type Workspace = Sandbox

/** @deprecated `WorkspaceCodeToolbox` is deprecated. Please use `SandboxCodeToolbox` instead. This will be removed in a future version. */
export type WorkspaceCodeToolbox = SandboxCodeToolbox

/** @deprecated `WorkspaceResources` is deprecated. Please use `SandboxResources` instead. This will be removed in a future version. */
export type WorkspaceResources = SandboxResources

/** @deprecated `WorkspaceState` is deprecated. Please use `SandboxState` instead. This will be removed in a future version. */
export type WorkspaceState = WS
/** @deprecated `WorkspaceState` is deprecated. Please use `SandboxState` instead. This will be removed in a future version. */
export const WorkspaceState = WS

/** @deprecated `WorkspaceTargetRegion` is deprecated. Please use `SandboxTargetRegion` instead. This will be removed in a future version. */
export const WorkspaceTargetRegion = CreateWorkspaceTargetEnum
/** @deprecated `WorkspaceTargetRegion` is deprecated. Please use `SandboxTargetRegion` instead. This will be removed in a future version. */
export type WorkspaceTargetRegion = CreateWorkspaceTargetEnum
