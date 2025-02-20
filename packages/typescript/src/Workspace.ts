/**
 * Core workspace functionality for Daytona.
 * 
 * Provides the main Workspace class that coordinates file system,
 * Git, process execution, and LSP functionality. It serves as the central point
 * for managing and interacting with Daytona workspaces.
 * 
 * The workspace must be in a 'started' state before performing operations.
 * 
 * @module Workspace
 * 
 * @example Basic workspace operations
 * // Create and initialize workspace
 * const daytona = new Daytona();
 * const workspace = await daytona.create();
 * 
 * // File operations
 * await workspace.fs.uploadFile(
 *   '/app/config.json',
 *   new File(['{"setting": "value"}'], 'config.json')
 * );
 * const contentBlob = await workspace.fs.downloadFile('/app/config.json');
 * 
 * // Git operations
 * await workspace.git.clone('https://github.com/user/repo.git');
 * 
 * // Process execution
 * const response = await workspace.process.executeCommand('ls -la');
 * console.log(response.result);
 * 
 * // LSP functionality
 * const lsp = workspace.createLspServer('typescript', '/workspace/project');
 * await lsp.didOpen('/workspace/project/src/index.ts');
 * const completions = await lsp.completions('/workspace/project/src/index.ts', {
 *   line: 10,
 *   character: 15
 * });
 * console.log(completions);
 * 
 */

import { ToolboxApi, WorkspaceApi } from '@daytonaio/api-client'
import { Workspace as WorkspaceInstance } from '@daytonaio/api-client'
import { FileSystem } from './FileSystem'
import { Git } from './Git'
//  import { LspLanguageId, LspServer } from './LspServer'
import { Process } from './Process'
import { LspLanguageId, LspServer } from './LspServer'

/**
 * Resources allocated to a workspace
 * 
 * @interface WorkspaceResources
 * @property {string} cpu - Number of CPU cores allocated (e.g., "1", "2")
 * @property {string | null} gpu - Number of GPUs allocated (e.g., "1") or null if no GPU
 * @property {string} memory - Amount of memory allocated with unit (e.g., "2Gi", "4Gi")
 * @property {string} disk - Amount of disk space allocated with unit (e.g., "10Gi", "20Gi")
 * 
 * @example
 * const resources: WorkspaceResources = {
 *   cpu: "2",
 *   gpu: "1",
 *   memory: "4Gi",
 *   disk: "20Gi"
 * };
 */
export interface WorkspaceResources {
  /** CPU allocation */
  cpu: string;
  /** GPU allocation */
  gpu: string | null;
  /** Memory allocation */
  memory: string;
  /** Disk allocation */
  disk: string;
}

/**
 * Structured information about a workspace
 * 
 * This interface provides detailed information about a workspace's configuration,
 * resources, and current state.
 * 
 * @interface WorkspaceInfo
 * @property {string} id - Unique identifier for the workspace
 * @property {string} name - Display name of the workspace
 * @property {string} image - Docker image used for the workspace
 * @property {string} user - OS user running in the workspace
 * @property {Record<string, string>} env - Environment variables set in the workspace
 * @property {Record<string, string>} labels - Custom labels attached to the workspace
 * @property {boolean} public - Whether the workspace is publicly accessible
 * @property {string} target - Target environment where the workspace runs
 * @property {WorkspaceResources} resources - Resource allocations for the workspace
 * @property {string} state - Current state of the workspace (e.g., "started", "stopped")
 * @property {string | null} errorReason - Error message if workspace is in error state
 * @property {string | null} snapshotState - Current state of workspace snapshot
 * @property {Date | null} snapshotStateCreatedAt - When the snapshot state was created
 * 
 * @example
 * const workspace = await daytona.create();
 * const info = await workspace.info();
 * console.log(`Workspace ${info.name} is ${info.state}`);
 * console.log(`Resources: ${info.resources.cpu} CPU, ${info.resources.memory} RAM`);
 */
export interface WorkspaceInfo {
  /** Unique identifier */
  id: string;
  /** Workspace name */
  name: string;
  /** Docker image */
  image: string;
  /** OS user */
  user: string;
  /** Environment variables */
  env: Record<string, string>;
  /** Workspace labels */
  labels: Record<string, string>;
  /** Public access flag */
  public: boolean;
  /** Target location */
  target: string;
  /** Resource allocations */
  resources: WorkspaceResources;
  /** Current state */
  state: string;
  /** Error reason if any */
  errorReason: string | null;
  /** Snapshot state */
  snapshotState: string | null;
  /** Snapshot state creation timestamp */
  snapshotStateCreatedAt: Date | null;
}

/**
 * Interface defining methods that a code toolbox must implement
 * @interface WorkspaceCodeToolbox
 */
export interface WorkspaceCodeToolbox {
  /** Generates a command to run the provided code */
  getRunCommand(code: string): string
}

/**
 * Represents a Daytona workspace.
 * 
 * A workspace provides file system operations, Git operations, process execution,
 * and LSP functionality. It serves as the main interface for interacting with
 * a Daytona workspace.
 * 
 * @property {string} id - Unique identifier for the workspace
 * @property {WorkspaceInstance} instance - The underlying workspace instance
 * @property {WorkspaceApi} workspaceApi - API client for workspace operations
 * @property {ToolboxApi} toolboxApi - API client for toolbox operations
 * @property {WorkspaceCodeToolbox} codeToolbox - Language-specific toolbox implementation
 * @property {FileSystem} fs - File system operations interface
 * @property {Git} git - Git operations interface
 * @property {Process} process - Process execution interface
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
   * 
   * @param {string} id - Unique identifier for the workspace
   * @param {WorkspaceInstance} instance - The underlying workspace instance
   * @param {WorkspaceApi} workspaceApi - API client for workspace operations
   * @param {ToolboxApi} toolboxApi - API client for toolbox operations
   * @param {WorkspaceCodeToolbox} codeToolbox - Language-specific toolbox implementation
   */
  constructor(
    public readonly id: string,
    public readonly instance: WorkspaceInstance,
    public readonly workspaceApi: WorkspaceApi,
    public readonly toolboxApi: ToolboxApi,
    private readonly codeToolbox: WorkspaceCodeToolbox,
  ) {
    this.fs = new FileSystem(instance, this.toolboxApi)
    this.git = new Git(this, this.toolboxApi, instance)
    this.process = new Process(this.codeToolbox, this.toolboxApi, instance)
  }

  /**
   * Gets the root directory path of the workspace.
   * 
   * @returns {Promise<string | undefined>} The absolute path to the workspace root directory
   * 
   * @example
   * const rootDir = await workspace.getWorkspaceRootDir();
   * console.log(`Workspace root: ${rootDir}`);
   */
  public async getWorkspaceRootDir(): Promise<string | undefined> {
    const response = await this.toolboxApi.getProjectDir(
      this.instance.id,
    )
    return response.data.dir
  }

  /**
   * Creates a new Language Server Protocol (LSP) server instance.
   * 
   * The LSP server provides language-specific features like code completion,
   * diagnostics, and more.
   * 
   * @param {LspLanguageId} languageId - The language server type (e.g., "typescript")
   * @param {string} pathToProject - Absolute path to the project root directory
   * @returns {LspServer} A new LSP server instance configured for the specified language
   * 
   * @example
   * const lsp = workspace.createLspServer('typescript', '/workspace/project');
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

  /**
   * Set labels for the workspace.
   * 
   * Labels are key-value pairs that can be used to organize and identify workspaces.
   * 
   * @param {Record<string, string>} labels - Dictionary of key-value pairs representing workspace labels
   * @returns {Promise<void>}
   * 
   * @example
   * // Set workspace labels
   * await workspace.setLabels({
   *   project: 'my-project',
   *   environment: 'development',
   *   team: 'backend'
   * });
   */
  public async setLabels(labels: Record<string, string>): Promise<void> {
    await this.workspaceApi.replaceLabels(this.instance.id, { labels })
  }
  
  /**
   * Start the workspace.
   * 
   * This method starts the workspace and waits for it to be ready.
   * 
   * @param {number} [timeout] - Maximum time to wait in seconds. 0 means no timeout.
   *                            Defaults to 60-second timeout.
   * @returns {Promise<void>}
   * @throws {Error} - `Error` - If workspace fails to start or times out
   * 
   * @example
   * const workspace = await daytona.getCurrentWorkspace('my-workspace');
   * await workspace.start(40);  // Wait up to 40 seconds
   * console.log('Workspace started successfully');
   */
  public async start(timeout?: number): Promise<void> {
    if (timeout != undefined && timeout < 0) {
      throw new Error('Timeout must be a non-negative number');
    }
    await this.workspaceApi.startWorkspace(this.instance.id)
    await this.waitUntilStarted(timeout)
  }

  /**
   * Stop the workspace.
   * 
   * This method stops the workspace and waits for it to be fully stopped.
   * 
   * @returns {Promise<void>}
   * 
   * @example
   * const workspace = await daytona.getCurrentWorkspace('my-workspace');
   * await workspace.stop();
   * console.log('Workspace stopped successfully');
   */
  public async stop(): Promise<void> {
    await this.workspaceApi.stopWorkspace(this.instance.id)
    await this.waitUntilStopped()
  }

  /**
   * Deletes the workspace
   * @returns {Promise<void>}
   */
  public async delete(): Promise<void> {
    await this.workspaceApi.deleteWorkspace(this.instance.id, true)
  }

  /**
   * Wait for workspace to reach 'started' state.
   * 
   * This method polls the workspace status until it reaches the 'started' state
   * or encounters an error.
   * 
   * @param {number} [timeout=60] - Maximum time to wait in seconds. 0 means no timeout.
   *                               Defaults to 60 seconds.
   * @returns {Promise<void>}
   * @throws {Error} - `Error` - If timeout is negative
   * @throws {Error} - `Error` - If workspace fails to start or times out
   * @throws {Error} - `Error` - If workspace fails to become ready within the timeout period
   */
  public async waitUntilStarted(timeout: number = 60) {
    if (timeout < 0) {
      throw new Error('Timeout must be a non-negative number');
    }

    const checkInterval = 100; // Wait 100 ms between checks
    const startTime = Date.now();

    while (timeout === 0 || (Date.now() - startTime) < (timeout * 1000)) {
      const response = await this.workspaceApi.getWorkspace(this.id);
      const state = response.data.state;

      if (state === 'started') {
        return;
      }

      if (state === 'error') {
        throw new Error(`Workspace failed to start with status: ${state}`);
      }

      await new Promise(resolve => setTimeout(resolve, checkInterval));
    }

    throw new Error('Workspace failed to become ready within the timeout period');
  }

  /**
   * Wait for workspace to reach 'stopped' state.
   * 
   * This method polls the workspace status until it reaches the 'stopped' state
   * or encounters an error. It will wait up to 60 seconds for the workspace to stop.
   * 
   * @returns {Promise<void>}
   * @throws {Error} - `Error` - If workspace fails to stop or times out
   */
  public async waitUntilStopped() {
    const maxAttempts = 600;
    let attempts = 0;

    while (attempts < maxAttempts) {
      const response = await this.workspaceApi.getWorkspace(this.id);
      const state = response.data.state;

      if (state === 'stopped') {
        return;
      }

      if (state === 'error') {
        throw new Error(`Workspace failed to stop with status: ${state}`);
      }

      await new Promise(resolve => setTimeout(resolve, 100)); // Wait 100 ms between checks
      attempts++;
    }

    throw new Error('Workspace failed to become stopped within the timeout period');
  }

  /**
   * Get structured information about the workspace.
   * 
   * @returns {Promise<WorkspaceInfo>} Detailed information about the workspace including its
   *                                   configuration, resources, and current state
   * 
   * @example
   * const info = await workspace.info();
   * console.log(`Workspace ${info.name}:`);
   * console.log(`State: ${info.state}`);
   * console.log(`Resources: ${info.resources.cpu} CPU, ${info.resources.memory} RAM`);
   */
  public async info(): Promise<WorkspaceInfo> {
    const response = await this.workspaceApi.getWorkspace(this.id)
    const instance = response.data
    const providerMetadata = JSON.parse(instance.info?.providerMetadata || '{}')

    // Extract resources with defaults
    const resourcesData = providerMetadata.resources || {}
    const resources: WorkspaceResources = {
      cpu: String(resourcesData.cpu || '1'),
      gpu: resourcesData.gpu ? String(resourcesData.gpu) : null,
      memory: String(resourcesData.memory || '2Gi'),
      disk: String(resourcesData.disk || '10Gi')
    }

    return {
      id: instance.id,
      name: instance.name,
      image: instance.image,
      user: instance.user,
      env: instance.env || {},
      labels: instance.labels || {},
      public: instance.public || false,
      target: instance.target,
      resources,
      state: providerMetadata.state || '',
      errorReason: providerMetadata.errorReason || null,
      snapshotState: providerMetadata.snapshotState || null,
      snapshotStateCreatedAt: providerMetadata.snapshotStateCreatedAt 
        ? new Date(providerMetadata.snapshotStateCreatedAt)
        : null
    }
  }

  /**
   * Set the auto-stop interval for the workspace.
   * 
   * The workspace will automatically stop after being idle (no new events) for the specified interval.
   * Events include any state changes or interactions with the workspace through the sdk.
   * Interactions using Workspace Previews are not included.
   * 
   * @param {number} interval - Number of minutes of inactivity before auto-stopping.
   *                           Set to 0 to disable auto-stop.
   * @returns {Promise<void>}
   * @throws {Error} - `Error` - If interval is not a non-negative integer
   * 
   * @example
   * // Auto-stop after 1 hour
   * await workspace.setAutostopInterval(60);
   * // Or disable auto-stop
   * await workspace.setAutostopInterval(0);
   */
  public async setAutostopInterval(interval: number): Promise<void> {
    if (!Number.isInteger(interval) || interval < 0) {
      throw new Error('autoStopInterval must be a non-negative integer');
    }
    
    await this.workspaceApi.setAutostopInterval(this.id, interval)
    this.instance.autoStopInterval = interval
  }
}
