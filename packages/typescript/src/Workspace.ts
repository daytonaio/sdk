import { ToolboxApi, WorkspaceApi } from '@daytonaio/api-client'
import { 
  WorkspaceStateEnum as WorkspaceState,
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
   * Sets labels for the workspace
   * @param {Record<string, string>} labels - The labels to set
   */
  public async setLabels(labels: Record<string, string>): Promise<void> {
    await this.workspaceApi.replaceLabels(this.instance.id, { labels })
  }
  
  /**
   * Starts the workspace
   * @param {number} timeout - Timeout in seconds (0 means no timeout, default is 60)
   * @returns {Promise<void>}
   */
  public async start(timeout: number = 60): Promise<void> {
    if (timeout < 0) {
      throw new DaytonaError('Timeout must be a non-negative number');
    }
    const startTime = Date.now();
    await this.workspaceApi.startWorkspace(this.instance.id, { timeout: timeout * 1000 })
    const timeElapsed = Date.now() - startTime;
    await this.waitUntilStarted(timeout - (timeElapsed / 1000))
  }

  /**
   * Stops the workspace
   * @param {number} timeout - Timeout in seconds (0 means no timeout, default is 60)
   * @returns {Promise<void>}
   */
  public async stop(timeout: number = 60): Promise<void> {
    if (timeout < 0) {
      throw new DaytonaError('Timeout must be a non-negative number');
    }
    const startTime = Date.now();
    await this.workspaceApi.stopWorkspace(this.instance.id, { timeout: timeout * 1000 })
    const timeElapsed = Date.now() - startTime;
    await this.waitUntilStopped(timeout - (timeElapsed / 1000))
  }

  /**
   * Deletes the workspace
   * @returns {Promise<void>}
   */
  public async delete(): Promise<void> {
    await this.workspaceApi.deleteWorkspace(this.instance.id, true)
  }

  /**
   * Waits until the workspace is started
   * @param {number} timeout - Timeout in seconds (0 means no timeout, default is 60)
   * @returns {Promise<void>}
   * @throws {DaytonaError} If the workspace ends up in an error state or fails to start within the timeout period
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
        throw new DaytonaError(`Workspace failed to start with status: ${state}`);
      }

      await new Promise(resolve => setTimeout(resolve, checkInterval));
    }

    throw new DaytonaError(`Workspace failed to become ready within the timeout period`);
  }

  /**
   * Waits until the workspace is stopped
   * @param {number} timeout - Timeout in seconds (0 means no timeout, default is 60)
   * @returns {Promise<void>}
   * @throws {DaytonaError} If the workspace fails to stop within the timeout period
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
        throw new DaytonaError(`Workspace failed to stop with status: ${state}`);
      }

      await new Promise(resolve => setTimeout(resolve, checkInterval));
    }

    throw new DaytonaError('Workspace failed to become stopped within the timeout period');
  }

  /**
   * Get structured information about the workspace
   * @returns {Promise<WorkspaceInfo>} Structured workspace information
   */
  public async info(): Promise<WorkspaceInfo> {
    const response = await this.workspaceApi.getWorkspace(this.id)
    const instance = response.data
    return Workspace.toWorkspaceInfo(instance)
  }

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
   * Sets the auto-stop interval for the workspace
   * @param {number} interval - Number of minutes after which the workspace will automatically stop (must be an integer). Set to 0 to disable auto-stop.
   * @throws {DaytonaError} If interval is negative
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
