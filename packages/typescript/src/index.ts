export { Daytona } from './Daytona'
export type { DaytonaConfig, CreateWorkspaceParams } from './Daytona'
export { CodeLanguage } from './Daytona'
export { Workspace } from './Workspace'
export type { WorkspaceCodeToolbox } from './Workspace'
export { FileSystem } from './FileSystem'
export { Git } from './Git'
export { Process } from './Process'
export { LspLanguageId } from './LspServer'
// export { LspServer } from './LspServer'
// export type { LspLanguageId, Position } from './LspServer'
export { DaytonaError } from './errors/DaytonaError'


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

export { WorkspaceState, CreateWorkspaceTargetEnum as WorkspaceTargetRegion } from '@daytonaio/api-client'
