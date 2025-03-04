/**
 * The Daytona SDK core Sandbox functionality.
 * 
 * Provides the main Workspace class representing a Daytona Sandbox that coordinates file system,
 * Git, process execution, and LSP functionality. It serves as the central point
 * for interacting with Daytona Sandboxes.
 * 
 * The Sandbox must be in a 'started' state before performing operations.
 * 
 * @module Workspace
 * 
 * @example
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
import { 
  WorkspaceState,
  Workspace as ApiWorkspace,
  WorkspaceInfo as ApiWorkspaceInfo,
  CreateWorkspaceTargetEnum as WorkspaceTargetRegion,
  CreateWorkspaceClassEnum as WorkspaceClass
} from '@daytonaio/api-client'
import { FileSystem } from './FileSystem'
import { Git } from './Git'
import { CodeRunParams, Process } from './Process'
import { LspLanguageId, LspServer } from './LspServer'
import { DaytonaError } from './errors/DaytonaError'

export interface WorkspaceInstance extends Omit<ApiWorkspace, 'info'> {
  info?: WorkspaceInfo;
}

/**
 * Resources allocated to a Sandbox
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
 * Structured information about a Sandbox
 * 
 * This interface provides detailed information about a Sandbox's configuration,
 * resources, and current state.
 * 
 * @interface WorkspaceInfo
 * @property {string} id - Unique identifier for the Sandbox
 * @property {string} name - Display name of the Sandbox
 * @property {string} image - Docker image used for the Sandbox
 * @property {string} user - OS user running in the Sandbox
 * @property {Record<string, string>} env - Environment variables set in the Sandbox
 * @property {Record<string, string>} labels - Custom labels attached to the Sandbox
 * @property {boolean} public - Whether the Sandbox is publicly accessible
 * @property {string} target - Target environment where the Sandbox runs
 * @property {WorkspaceResources} resources - Resource allocations for the Sandbox
 * @property {string} state - Current state of the Sandbox (e.g., "started", "stopped")
 * @property {string | null} errorReason - Error message if Sandbox is in error state
 * @property {string | null} snapshotState - Current state of Sandbox snapshot
 * @property {Date | null} snapshotStateCreatedAt - When the snapshot state was created
 * 
 * @example
 * const workspace = await daytona.create();
 * const info = await workspace.info();
 * console.log(`Workspace ${info.name} is ${info.state}`);
 * console.log(`Resources: ${info.resources.cpu} CPU, ${info.resources.memory} RAM`);
 */
export interface WorkspaceInfo extends ApiWorkspaceInfo {
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
  target: WorkspaceTargetRegion | string;
  /** Resource allocations */
  resources: WorkspaceResources;
  /** Current state */
  state: WorkspaceState;
  /** Error reason if any */
  errorReason: string | null;
  /** Snapshot state */
  snapshotState: string | null;
  /** Snapshot state creation timestamp */
  snapshotStateCreatedAt: Date | null;
  /** Node domain */
  nodeDomain: string;
  /** Region */
  region: WorkspaceTargetRegion;
  /** Class */
  class: WorkspaceClass;
  /** Updated at */
  updatedAt: string;
  /** Last snapshot */
  lastSnapshot: string | null;
  /** Auto-stop interval in minutes*/
  autoStopInterval: number;
  /**
   * @deprecated Use `state`, `nodeDomain`, `region`, `class`, `updatedAt`, `lastSnapshot`, `resources`, `autoStopInterval` instead.
   */
  providerMetadata?: string;
}
/**
 * Interface defining methods that a code toolbox must implement
 * @interface WorkspaceCodeToolbox
 */
export interface WorkspaceCodeToolbox {
  /** Generates a command to run the provided code */
  getRunCommand(code: string, params?: CodeRunParams): string
}

/**
 * Represents a Daytona Sandbox.
 * 
 * A Sandbox provides file system operations, Git operations, process execution,
 * and LSP functionality. It serves as the main interface for interacting with
 * a Daytona workspace.
 * 
 * @property {string} id - Unique identifier for the Sandbox
 * @property {WorkspaceInstance} instance - The underlying Sandbox instance
 * @property {WorkspaceApi} workspaceApi - API client for Sandbox operations
 * @property {ToolboxApi} toolboxApi - API client for toolbox operations
 * @property {WorkspaceCodeToolbox} codeToolbox - Language-specific toolbox implementation
 * @property {FileSystem} fs - File system operations interface
 * @property {Git} git - Git operations interface
 * @property {Process} process - Process execution interface
 */
export class Workspace {
  /** File system operations for the Sandbox */
  public readonly fs: FileSystem
  /** Git operations for the Sandbox */
  public readonly git: Git
  /** Process and code execution operations */
  public readonly process: Process

  /**
   * Creates a new Sandbox instance
   * 
   * @param {string} id - Unique identifier for the Sandbox
   * @param {WorkspaceInstance} instance - The underlying Sandbox instance
   * @param {WorkspaceApi} workspaceApi - API client for Sandbox operations
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
   * Gets the root directory path of the Sandbox.
   * 
   * @returns {Promise<string | undefined>} The absolute path to the Sandbox root directory
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
    languageId: LspLanguageId | string,
    pathToProject: string,
  ): LspServer {
    return new LspServer(
      languageId as LspLanguageId,
      pathToProject,
      this.toolboxApi,
      this.instance,
    )
  }

  /**
   * Sets labels for the Sandbox.
   * 
   * Labels are key-value pairs that can be used to organize and identify Sandboxes.
   * 
   * @param {Record<string, string>} labels - Dictionary of key-value pairs representing Sandbox labels
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
   * Start the Sandbox.
   * 
   * This method starts the Sandbox and waits for it to be ready.
   * 
   * @param {number} [timeout] - Maximum time to wait in seconds. 0 means no timeout.
   *                            Defaults to 60-second timeout.
   * @returns {Promise<void>}
   * @throws {DaytonaError} - `DaytonaError` - If Sandbox fails to start or times out
   * 
   * @example
   * const workspace = await daytona.getCurrentWorkspace('my-workspace');
   * await workspace.start(40);  // Wait up to 40 seconds
   * console.log('Workspace started successfully');
   */
  public async start(timeout: number = 60): Promise<void> {
    if (timeout < 0) {
      throw new DaytonaError('Timeout must be a non-negative number');
    }
    const startTime = Date.now();
    await this.workspaceApi.startWorkspace(this.instance.id, { timeout: timeout * 1000 })
    const timeElapsed = Date.now() - startTime;
    await this.waitUntilStarted(timeout ? timeout - (timeElapsed / 1000) : 0)
  }

  /**
   * Stops the Sandbox.
   * 
   * This method stops the Sandbox and waits for it to be fully stopped.
   * 
   * @param {number} [timeout] - Maximum time to wait in seconds. 0 means no timeout.
   *                            Defaults to 60-second timeout.
   * @returns {Promise<void>}
   * 
   * @example
   * const workspace = await daytona.getCurrentWorkspace('my-workspace');
   * await workspace.stop();
   * console.log('Workspace stopped successfully');
   */
  public async stop(timeout: number = 60): Promise<void> {
    if (timeout < 0) {
      throw new DaytonaError('Timeout must be a non-negative number');
    }
    const startTime = Date.now();
    await this.workspaceApi.stopWorkspace(this.instance.id, { timeout: timeout * 1000 })
    const timeElapsed = Date.now() - startTime;
    await this.waitUntilStopped(timeout ? timeout - (timeElapsed / 1000) : 0)
  }

  /**
   * Deletes the Sandbox.
   * @returns {Promise<void>}
   */
  public async delete(): Promise<void> {
    await this.workspaceApi.deleteWorkspace(this.instance.id, true)
  }

  /**
   * Waits for the Sandbox to reach the 'started' state.
   * 
   * This method polls the Sandbox status until it reaches the 'started' state
   * or encounters an error.
   * 
   * @param {number} [timeout] - Maximum time to wait in seconds. 0 means no timeout.
   *                               Defaults to 60 seconds.
   * @returns {Promise<void>}
   * @throws {DaytonaError} - `DaytonaError` - If the workspace ends up in an error state or fails to start within the timeout period.
   */
  public async waitUntilStarted(timeout: number = 60) {
    if (timeout < 0) {
      throw new DaytonaError('Timeout must be a non-negative number');
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
        throw new DaytonaError(`Workspace failed to start with status: ${state}, error reason: ${response.data.errorReason}`);
      }

      await new Promise(resolve => setTimeout(resolve, checkInterval));
    }

    throw new DaytonaError(`Workspace failed to become ready within the timeout period`);
  }

  /**
   * Wait for Sandbox to reach 'stopped' state.
   * 
   * This method polls the Sandbox status until it reaches the 'stopped' state
   * or encounters an error.
   * 
   * @param {number} [timeout] - Maximum time to wait in seconds. 0 means no timeout.
   *                               Defaults to 60 seconds.
   * @returns {Promise<void>}
   * @throws {DaytonaError} - `DaytonaError` - If the workspace fails to stop within the timeout period.
   */
  public async waitUntilStopped(timeout: number = 60) {
    if (timeout < 0) {
      throw new DaytonaError('Timeout must be a non-negative number');
    }

    const checkInterval = 100; // Wait 100 ms between checks
    const startTime = Date.now();

    while (timeout === 0 || (Date.now() - startTime) < (timeout * 1000)) {
      const response = await this.workspaceApi.getWorkspace(this.id);
      const state = response.data.state;

      if (state === 'stopped') {
        return;
      }

      if (state === 'error') {
        throw new DaytonaError(`Workspace failed to stop with status: ${state}, error reason: ${response.data.errorReason}`);
      }

      await new Promise(resolve => setTimeout(resolve, checkInterval));
    }

    throw new DaytonaError('Workspace failed to become stopped within the timeout period');
  }

  /**
   * Gets structured information about the Sandbox.
   * 
   * @returns {Promise<WorkspaceInfo>} Detailed information about the Sandbox including its
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
    return Workspace.toWorkspaceInfo(instance)
  }

  /**
   * Converts an API workspace instance to a WorkspaceInfo object.
   * 
   * @param {ApiWorkspace} instance - The API workspace instance to convert
   * @returns {WorkspaceInfo} The converted WorkspaceInfo object
   */
  public static toWorkspaceInfo(instance: ApiWorkspace): WorkspaceInfo {
    const providerMetadata = JSON.parse(instance.info?.providerMetadata || '{}')
    var resourcesData = providerMetadata.resources || providerMetadata

    // Extract resources with defaults
    const resources: WorkspaceResources = {
      cpu: String(resourcesData.cpu || '1'),
      gpu: resourcesData.gpu ? String(resourcesData.gpu) : null,
      memory: `${resourcesData.memory ?? 2}Gi`,
      disk: `${resourcesData.disk ?? 10}Gi`
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
        : null,
      nodeDomain: providerMetadata.nodeDomain || '',
      region: providerMetadata.region || '',
      class: providerMetadata.class || '',
      updatedAt: providerMetadata.updatedAt || '',
      lastSnapshot: providerMetadata.lastSnapshot || null,
      autoStopInterval: providerMetadata.autoStopInterval || 0,
      created: instance.info?.created || '',
      providerMetadata: instance.info?.providerMetadata,
    }
  }

  /**
   * Set the auto-stop interval for the Sandbox.
   * 
   * The Sandbox will automatically stop after being idle (no new events) for the specified interval.
   * Events include any state changes or interactions with the Sandbox through the sdk.
   * Interactions using Sandbox Previews are not included.
   * 
   * @param {number} interval - Number of minutes of inactivity before auto-stopping.
   *                           Set to 0 to disable auto-stop. Default is 15 minutes.
   * @returns {Promise<void>}
   * @throws {DaytonaError} - `DaytonaError` - If interval is not a non-negative integer
   * 
   * @example
   * // Auto-stop after 1 hour
   * await workspace.setAutostopInterval(60);
   * // Or disable auto-stop
   * await workspace.setAutostopInterval(0);
   */
  public async setAutostopInterval(interval: number): Promise<void> {
    if (!Number.isInteger(interval) || interval < 0) {
      throw new DaytonaError('autoStopInterval must be a non-negative integer');
    }
    
    await this.workspaceApi.setAutostopInterval(this.id, interval)
    this.instance.autoStopInterval = interval
  }

  /**
   * Gets the preview link for the workspace at a specific port. If the port is not open, it will open it and return the link.
   * @param {number} port - The port to open the preview link on
   * @returns {string} The preview link for the workspace at the specified port
   * @throws {DaytonaError} If the node domain is not found in the provider metadata
   */
  public getPreviewLink(port: number): string {
    const providerMetadata = JSON.parse(this.instance.info?.providerMetadata || '{}')
    const nodeDomain = providerMetadata.nodeDomain || ''
    if (!nodeDomain) {
      throw new DaytonaError("Cannot get preview link. Node domain not found in provider metadata. Please contact support.")
    }
    return `https://${port}-${this.id}.${nodeDomain}`
  }
}
