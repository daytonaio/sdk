import { Workspace as WorkspaceInstance, WorkspaceToolboxApi } from './client'
import { FileSystem } from './FileSystem'
import { Git } from './Git'
import { LspLanguageId, LspServer } from './LspServer'
import { Process } from './Process'

/**
 * Interface defining methods that a code toolbox must implement
 * @interface WorkspaceCodeToolbox
 */
export interface WorkspaceCodeToolbox {
  /** Gets the default Docker image for this language */
  getDefaultImage(): string
  /** Generates a command to run the provided code */
  getRunCommand(code: string): string
}

/**
 * Represents a Daytona workspace instance with file system, git, and process management capabilities
 * @class Workspace
 */
export class Workspace {
  /** File system operations for the workspace */
  public readonly fs: FileSystem
  /** Git operations for the workspace */
  public readonly git: Git
  /** Process and code execution operations */
  public readonly process: Process

  /**
   * Creates a new workspace instance
   * @param {string} id - Unique identifier for the workspace
   * @param {WorkspaceInstance} instance - The underlying workspace instance
   * @param {WorkspaceToolboxApi} toolboxApi - API client for workspace operations
   * @param {WorkspaceCodeToolbox} codeToolbox - Language-specific toolbox implementation
   */
  constructor(
    public readonly id: string,
    private readonly instance: WorkspaceInstance,
    public readonly toolboxApi: WorkspaceToolboxApi,
    private readonly codeToolbox: WorkspaceCodeToolbox,
  ) {
    this.fs = new FileSystem(instance, this.toolboxApi)
    this.git = new Git(this, this.toolboxApi, instance)
    this.process = new Process(this.codeToolbox, this.toolboxApi, instance)
  }

  /**
   * Gets the root directory path of the workspace
   * @returns {Promise<string>} The absolute path to the workspace root
   */
  public async getWorkspaceRootDir(): Promise<string> {
    const response = await this.toolboxApi.getProjectDir({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
    })
    return response.dir!
  }

  /**
   * Creates a new Language Server Protocol (LSP) server instance
   * @param {LspLanguageId} languageId - The language server type
   * @param {string} pathToProject - Path to the project root
   * @returns {LspServer} A new LSP server instance
   */
  public createLspServer(
    languageId: LspLanguageId,
    pathToProject: string,
  ): LspServer {
    return new LspServer(
      languageId,
      pathToProject,
      this.toolboxApi,
      this.instance,
    )
  }
}
