import {
  CompletionList,
  LspSymbol,
  Workspace as WorkspaceInstance,
  WorkspaceToolboxApi,
} from './client'

/**
 * Supported language server types
 * @typedef {('typescript')} LspLanguageId
 */
export type LspLanguageId = 'typescript'

/**
 * Position in a text document
 * @interface Position
 */
export type Position = {
  /** Zero-based line number */
  line: number
  /** Zero-based character offset */
  character: number
}

/**
 * Provides Language Server Protocol (LSP) functionality
 * @class LspServer
 */
export class LspServer {
  constructor(
    private readonly languageId: LspLanguageId,
    private readonly pathToProject: string,
    private readonly toolboxApi: WorkspaceToolboxApi,
    private readonly instance: WorkspaceInstance,
  ) {}

  /**
   * Starts the language server
   * @returns {Promise<void>}
   */
  public async start(): Promise<void> {
    return this.toolboxApi.lspStart({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      params: {
        languageId: this.languageId,
        pathToProject: this.pathToProject,
      },
    })
  }

  /**
   * Stops the language server
   * @returns {Promise<void>}
   */
  public async stop(): Promise<void> {
    return this.toolboxApi.lspStop({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      params: {
        languageId: this.languageId,
        pathToProject: this.pathToProject,
      },
    })
  }

  /**
   * Notifies the server that a file has been opened
   * @param {string} path - Path to the opened file
   * @returns {Promise<void>}
   */
  public async didOpen(path: string): Promise<void> {
    return this.toolboxApi.lspDidOpen({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      params: {
        languageId: this.languageId,
        pathToProject: this.pathToProject,
        uri: 'file://' + path,
      },
    })
  }

  /**
   * Notifies the server that a file has been closed
   * @param {string} path - Path to the closed file
   * @returns {Promise<void>}
   */
  public async didClose(path: string): Promise<void> {
    return this.toolboxApi.lspDidClose({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      params: {
        languageId: this.languageId,
        pathToProject: this.pathToProject,
        uri: 'file://' + path,
      },
    })
  }

  /**
   * Gets document symbols (functions, classes, etc.)
   * @param {string} path - Path to the file
   * @returns {Promise<LspSymbol[]>} Array of document symbols
   */
  public async documentSymbols(path: string): Promise<LspSymbol[]> {
    return this.toolboxApi.lspDocumentSymbols({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      languageId: this.languageId,
      pathToProject: this.pathToProject,
      uri: 'file://' + path,
    })
  }

  /**
   * Searches for symbols across the workspace
   * @param {string} query - Search query
   * @returns {Promise<LspSymbol[]>} Array of matching symbols
   */
  public async workspaceSymbols(query: string): Promise<LspSymbol[]> {
    return this.toolboxApi.lspWorkspaceSymbols({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      languageId: this.languageId,
      pathToProject: this.pathToProject,
      query,
    })
  }

  /**
   * Gets code completion suggestions
   * @param {string} path - Path to the file
   * @param {Position} position - Cursor position
   * @returns {Promise<CompletionList>} List of completion suggestions
   */
  public async completions(
    path: string,
    position: Position,
  ): Promise<CompletionList> {
    return this.toolboxApi.lspCompletions({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      params: {
        languageId: this.languageId,
        pathToProject: this.pathToProject,
        uri: 'file://' + path,
        position,
      },
    })
  }
}
