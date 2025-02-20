/**
 * The Daytona SDK provides Language Server Protocol (LSP) support through Sandbox instances.
 * This enables advanced language features like code completion, diagnostics, and more.
 * 
 * The LSP server must be started with start() before using any other methods,
 * and should be stopped with stop() when no longer needed to free resources.
 * 
 * @module LspServer
 * 
 * @example
 * // Basic LSP server usage
 * // Create and initialize workspace
 * const workspace = await daytona.create();
 * 
 * // Create and start LSP server
 * const lsp = workspace.createLspServer('typescript', '/workspace/project');
 * await lsp.start();
 * 
 * // Open a file for editing
 * await lsp.didOpen('/workspace/project/src/index.ts');
 * 
 * // Get completions at a position
 * const completions = await lsp.completions(
 *   '/workspace/project/src/index.ts',
 *   { line: 10, character: 15 }
 * );
 * console.log('Completions:', completions);
 * 
 * // Get document symbols
 * const symbols = await lsp.documentSymbols('/workspace/project/src/index.ts');
 * symbols.forEach(symbol => {
 *   console.log(`${symbol.name}: ${symbol.kind}`);
 * });
 * 
 * // Clean up
 * await lsp.didClose('/workspace/project/src/index.ts');
 * await lsp.stop();
 * 
 */

import {
  CompletionList,
  LspSymbol,
  ToolboxApi,
} from '@daytonaio/api-client'
import { WorkspaceInstance } from './Workspace'

/**
 * Supported language server types.
 */
export enum LspLanguageId {
  PYTHON = 'python',
  TYPESCRIPT = 'typescript',
  JAVASCRIPT = 'javascript',
}

/**
 * Represents a position in a text document.
 * 
 * This interface represents a zero-based position within a text document,
 * specified by line number and character offset.
 * 
 * @interface Position
 * @property {number} line - Zero-based line number in the document
 * @property {number} character - Zero-based character offset on the line
 * 
 * @example
 * const position: Position = {
 *   line: 10,     // Line 11 (zero-based)
 *   character: 15  // Character 16 on the line (zero-based)
 * };
 */
export type Position = {
  /** Zero-based line number */
  line: number
  /** Zero-based character offset */
  character: number
}

/**
 * Provides Language Server Protocol functionality for code intelligence.
 * 
 * This class implements a subset of the Language Server Protocol (LSP) to provide
 * IDE-like features such as code completion, symbol search, and more.
 * 
 * @class LspServer
 * 
 * @property {LspLanguageId} languageId - The language server type (e.g., "typescript")
 * @property {string} pathToProject - Absolute path to the project root directory
 * @property {ToolboxApi} toolboxApi - API client for Sandbox operations
 * @property {WorkspaceInstance} instance - The Sandbox instance this server belongs to
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
   * Starts the language server.
   * 
   * This method must be called before using any other LSP functionality.
   * It initializes the language server for the specified language and project.
   * 
   * @returns {Promise<void>}
   * 
   * @example
   * const lsp = workspace.createLspServer('typescript', '/workspace/project');
   * await lsp.start();  // Initialize the server
   * // Now ready for LSP operations
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
   * Stops the language server.
   * 
   * This method should be called when the LSP server is no longer needed to
   * free up system resources.
   * 
   * @returns {Promise<void>}
   * 
   * @example
   * // When done with LSP features
   * await lsp.stop();  // Clean up resources
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
   * Notifies the language server that a file has been opened.
   * 
   * This method should be called when a file is opened in the editor to enable
   * language features like diagnostics and completions for that file. The server
   * will begin tracking the file's contents and providing language features.
   * 
   * @param {string} path - Absolute path to the opened file
   * @returns {Promise<void>}
   * 
   * @example
   * // When opening a file for editing
   * await lsp.didOpen('/workspace/project/src/index.ts');
   * // Now can get completions, symbols, etc. for this file
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
   * Notifies the language server that a file has been closed.
   * 
   * This method should be called when a file is closed in the editor to allow
   * the language server to clean up any resources associated with that file.
   * 
   * @param {string} path - Absolute path to the closed file
   * @returns {Promise<void>}
   * 
   * @example
   * // When done editing a file
   * await lsp.didClose('/workspace/project/src/index.ts');
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
   * Get symbol information from a document.
   * 
   * This method returns information about all symbols (functions, classes,
   * variables, etc.) defined in the specified document.
   * 
   * @param {string} path - Absolute path to the file to get symbols from
   * @returns {Promise<LspSymbol[]>} List of symbols in the document. Each symbol includes:
   *                                 - name: The symbol's name
   *                                 - kind: The symbol's kind (function, class, variable, etc.)
   *                                 - location: The location of the symbol in the file
   * 
   * @example
   * // Get all symbols in a file
   * const symbols = await lsp.documentSymbols('/workspace/project/src/index.ts');
   * symbols.forEach(symbol => {
   *   console.log(`${symbol.kind} ${symbol.name}: ${symbol.location}`);
   * });
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
   * Searches for symbols across the entire Sandbox.
   * 
   * This method searches for symbols matching the query string across all files
   * in the Sandbox. It's useful for finding declarations and definitions
   * without knowing which file they're in.
   * 
   * @param {string} query - Search query to match against symbol names
   * @returns {Promise<LspSymbol[]>} List of matching symbols from all files. Each symbol includes:
   *                                 - name: The symbol's name
   *                                 - kind: The symbol's kind (function, class, variable, etc.)
   *                                 - location: The location of the symbol in the file
   * 
   * @example
   * // Search for all symbols containing "User"
   * const symbols = await lsp.workspaceSymbols('User');
   * symbols.forEach(symbol => {
   *   console.log(`${symbol.name} (${symbol.kind}) in ${symbol.location}`);
   * });
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
   * Gets completion suggestions at a position in a file.
   * 
   * @param {string} path - Absolute path to the file
   * @param {Position} position - The position in the file where completion was requested
   * @returns {Promise<CompletionList>} List of completion suggestions. The list includes:
   *                                    - isIncomplete: Whether more items might be available
   *                                    - items: List of completion items, each containing:
   *                                      - label: The text to insert
   *                                      - kind: The kind of completion
   *                                      - detail: Additional details about the item
   *                                      - documentation: Documentation for the item
   *                                      - sortText: Text used to sort the item in the list
   *                                      - filterText: Text used to filter the item
   *                                      - insertText: The actual text to insert (if different from label)
   * 
   * @example
   * // Get completions at a specific position
   * const completions = await lsp.completions('/workspace/project/src/index.ts', {
   *   line: 10,
   *   character: 15
   * });
   * completions.items.forEach(item => {
   *   console.log(`${item.label} (${item.kind}): ${item.detail}`);
   * });
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
