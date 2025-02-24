import { ToolboxApi, WorkspaceApi } from '@daytonaio/api-client'
import { Workspace as WorkspaceInstance } from '@daytonaio/api-client'
import { FileSystem } from './FileSystem'
import { Git } from './Git'
//  import { LspLanguageId, LspServer } from './LspServer'
import { Process } from './Process'
import { LspLanguageId, LspServer } from './LspServer'

/**
 * Resources allocated to a workspace
 * @interface WorkspaceResources
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
 * @interface WorkspaceInfo
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
   * @param {WorkspaceApi} workspaceApi - API client for workspace operations
   * @param {ToolboxApi} toolboxApi - API client for toolbox operations
   * 
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
   * Gets the root directory path of the workspace
   * @returns {Promise<string>} The absolute path to the workspace root
   */
  public async getWorkspaceRootDir(): Promise<string | undefined> {
    const response = await this.toolboxApi.getProjectDir(
      this.instance.id,
    )
    return response.data.dir
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

  /**
   * Sets labels for the workspace
   * @param {Record<string, string>} labels - The labels to set
   */
  public async setLabels(labels: Record<string, string>): Promise<void> {
    await this.workspaceApi.replaceLabels(this.instance.id, { labels })
  }
  
  /**
   * Starts the workspace
   * @returns {Promise<void>}
   */
  public async start(timeout?: number): Promise<void> {
    if (timeout != undefined && timeout < 0) {
      throw new Error('Timeout must be a non-negative number');
    }
    await this.workspaceApi.startWorkspace(this.instance.id)
    await this.waitUntilStarted(timeout)
  }

  /**
   * Stops the workspace
   * @returns {Promise<void>}
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
   * Get structured information about the workspace
   * @returns {Promise<WorkspaceInfo>} Structured workspace information
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
   * Sets the auto-stop interval for the workspace
   * @param {number} interval - Number of minutes after which the workspace will automatically stop (must be an integer). Set to 0 to disable auto-stop.
   * @throws {Error} If interval is negative
   */
  public async setAutostopInterval(interval: number): Promise<void> {
    if (!Number.isInteger(interval) || interval < 0) {
      throw new Error('autoStopInterval must be a non-negative integer');
    }
    
    await this.workspaceApi.setAutostopInterval(this.id, interval)
    this.instance.autoStopInterval = interval
  }

  /**
   * Gets the preview link for the workspace at a specific port. If the port is not open, it will open it and return the link.
   * @param {number} port - The port to open the preview link on
   * @returns {string} The preview link for the workspace at the specified port
   * @throws {Error} If the node domain is not found in the provider metadata
   */
  public getPreviewLink(port: number): string {
    const providerMetadata = JSON.parse(this.instance.info?.providerMetadata || '{}')
    const nodeDomain = providerMetadata.nodeDomain || ''
    if (!nodeDomain) {
      throw new Error("Cannot get preview link. Node domain not found in provider metadata. Please contact support.")
    }
    return `https://${port}-${this.id}.${nodeDomain}`
  }
}
