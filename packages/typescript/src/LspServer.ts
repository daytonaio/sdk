import {
  CompletionList,
  LspSymbol,
  ToolboxApi,
} from '@daytonaio/api-client'
import { WorkspaceInstance } from './Workspace'

/**
 * Supported language server types
 * @typedef {('typescript')} LspLanguageId
 */
export enum LspLanguageId {
  PYTHON = 'python',
  TYPESCRIPT = 'typescript',
  JAVASCRIPT = 'javascript',
}

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
    private readonly toolboxApi: ToolboxApi,
    private readonly instance: WorkspaceInstance,
  ) {
    if (!Object.values(LspLanguageId).includes(this.languageId)) {
      throw new Error(`Invalid languageId: ${this.languageId}. Supported values are: ${Object.values(LspLanguageId).join(', ')}`);
    }
  }

  /**
   * Starts the language server
   * @returns {Promise<void>}
   */
  public async start(): Promise<void> {
    await this.toolboxApi.lspStart(
      this.instance.id,
      {
        languageId: this.languageId,
        pathToProject: this.pathToProject,
      })
  }

  /**
   * Stops the language server
   * @returns {Promise<void>}
   */
  public async stop(): Promise<void> {
    await this.toolboxApi.lspStop(
      this.instance.id,
      {
        languageId: this.languageId,
        pathToProject: this.pathToProject,
      },
    )
  }

  /**
   * Notifies the server that a file has been opened
   * @param {string} path - Path to the opened file
   * @returns {Promise<void>}
   */
  public async didOpen(path: string): Promise<void> {
    await this.toolboxApi.lspDidOpen(
      this.instance.id,
      {
        languageId: this.languageId,
        pathToProject: this.pathToProject,
        uri: 'file://' + path,
      },
    )
  }

  /**
   * Notifies the server that a file has been closed
   * @param {string} path - Path to the closed file
   * @returns {Promise<void>}
   */
  public async didClose(path: string): Promise<void> {
    await this.toolboxApi.lspDidClose(
      this.instance.id,
      {
        languageId: this.languageId,
        pathToProject: this.pathToProject,
        uri: 'file://' + path,
      },
    )
  }

  /**
   * Gets document symbols (functions, classes, etc.)
   * @param {string} path - Path to the file
   * @returns {Promise<LspSymbol[]>} Array of document symbols
   */
  public async documentSymbols(path: string): Promise<LspSymbol[]> {
    const response = await this.toolboxApi.lspDocumentSymbols(
      this.instance.id,
      this.languageId,
      this.pathToProject,
      'file://' + path,
    )
    return response.data
  }

  /**
   * Searches for symbols across the workspace
   * @param {string} query - Search query
   * @returns {Promise<LspSymbol[]>} Array of matching symbols
   */
  public async workspaceSymbols(query: string): Promise<LspSymbol[]> {
    const response = await this.toolboxApi.lspWorkspaceSymbols(
      this.instance.id,
      this.languageId,
      this.pathToProject,
      query,
    )
    return response.data
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
    const response = await this.toolboxApi.lspCompletions(
      this.instance.id,
      {
        languageId: this.languageId,
        pathToProject: this.pathToProject,
        uri: 'file://' + path,
        position,
      },
    )
    return response.data
  }
}
