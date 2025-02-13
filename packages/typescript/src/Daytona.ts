import { v4 as uuidv4 } from 'uuid'

import { WorkspacePythonCodeToolbox } from './code-toolbox/WorkspacePythonCodeToolbox'
import { Workspace } from './Workspace'
import {
  Configuration,
  WorkspaceApi,
  ToolboxApi,
  CreateWorkspaceTargetEnum,
} from '@daytonaio/api-client'
import { WorkspaceTsCodeToolbox } from './code-toolbox/WorkspaceTsCodeToolbox'
import { AxiosError } from 'axios'
import { TimeoutError } from './utils/errors'
/**
 * Configuration options for initializing the Daytona client
 * @interface DaytonaConfig
 */
export interface DaytonaConfig {
  /** API key for authentication with Daytona server */
  apiKey: string
  /** URL of the Daytona server */
  serverUrl: string
  /** Target environment for workspaces */
  target: CreateWorkspaceTargetEnum
}

/** 
 * Supported programming languages for code execution
 */
export type CodeLanguage = 'python' | 'javascript' | 'typescript'

/**
 * Resource allocation for a workspace
 * @interface WorkspaceResources
 */
export interface WorkspaceResources {
  /** CPU allocation for the workspace */
  cpu?: number
  /** GPU allocation for the workspace */
  gpu?: number
  /** Memory allocation for the workspace in MB */
  memory?: number
  /** Disk space allocation for the workspace in MB */
  disk?: number
}

/**
 * Parameters for creating a new workspace
 * @interface CreateWorkspaceParams
 */
export type CreateWorkspaceParams = {
  /** Optional workspace ID. If not provided, a random ID will be generated */
  id?: string
  /** Optional Docker image to use for the workspace */
  image?: string
  /** Optional os user to use for the workspace */
  user?: string
  /** Programming language for direct code execution */
  language?: CodeLanguage
  /** Optional environment variables to set in the workspace */
  envVars?: Record<string, string>
  /** Workspace labels */
  labels?: Record<string, string>
  /** Is the workspace port preview public */
  public?: boolean
  /** Target location for the workspace */
  target?: string
  /** Resource allocation for the workspace */
  resources?: WorkspaceResources
  /** If true, will not wait for the workspace to be ready before returning */
  async?: boolean
  /**
   * Timeout in seconds, for the workspace to be ready (0 means no timeout)
   * @deprecated Use methods with `timeout` parameter instead
   */
  timeout?: number
  /** Auto-stop interval in minutes (0 means disabled) (must be a non-negative integer) */
  autoStopInterval?: number
}

/**
 * Main class for interacting with Daytona Server API
 * @class Daytona
 */
export class Daytona {
  private readonly workspaceApi: WorkspaceApi
  private readonly toolboxApi: ToolboxApi
  private readonly target: CreateWorkspaceTargetEnum

  private readonly apiKey: string
  private readonly serverUrl: string

  /**
   * Creates a new Daytona client instance
   * @param {DaytonaConfig} [config] - Configuration options
   * @throws {Error} When API key or server URL is missing
   */
  constructor(config?: DaytonaConfig) {
    const apiKey = config?.apiKey || process.env.DAYTONA_API_KEY
    if (!apiKey) {
      throw new Error('API key is required')
    }
    const serverUrl = config?.serverUrl || process.env.DAYTONA_SERVER_URL
    if (!serverUrl) {
      throw new Error('Server URL is required')
    }
    const envTarget = process.env.DAYTONA_TARGET as CreateWorkspaceTargetEnum
    const target = config?.target || envTarget

    this.apiKey = apiKey
    this.serverUrl = serverUrl
    this.target = target

    const configuration = new Configuration({
      basePath: this.serverUrl,
      baseOptions: {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
        },
      },
    })

    this.workspaceApi = new WorkspaceApi(configuration)
    this.toolboxApi = new ToolboxApi(configuration)
  }

  /**
   * Creates a new workspace
   * @param {CreateWorkspaceParams} [params] - Parameters for workspace creation
   * @param {number} [timeout] - Timeout in seconds (0 means no timeout, default is 60)
   * @returns {Promise<Workspace>} The created workspace instance
   */
  public async create(params: CreateWorkspaceParams, timeout: number = 60): Promise<Workspace> {
    const startTime = Date.now();

    if (timeout < 0) {
      throw new Error('Timeout must be a non-negative number');
    }

    if (params == null) {
      params = { language: 'python' }
    }

    params.id = params.id || `sandbox-${uuidv4().slice(0, 8)}`

    // remove this when params.timeout is removed
    const effectiveTimeout = params.timeout || timeout

    if (params.autoStopInterval !== undefined && (!Number.isInteger(params.autoStopInterval) || params.autoStopInterval < 0)) {
      throw new Error('autoStopInterval must be a non-negative integer');
    }

    const codeToolbox = this.getCodeToolbox(params?.language)

    try {
      const response = await this.workspaceApi.createWorkspace({
          id: params.id,
          name: params.id,
          image: params.image,
          user: params.user,
          env: params.envVars || {},
          labels: params.labels,
          public: params.public,
          target: this.target,
          cpu: params.resources?.cpu,
          gpu: params.resources?.gpu,
          memory: params.resources?.memory,
          disk: params.resources?.disk,
          autoStopInterval: params.autoStopInterval,
        },
        {
          timeout: effectiveTimeout * 1000
        })

      const workspaceInstance = response.data

      const workspace = new Workspace(
        params.id!,
        workspaceInstance,
        this.workspaceApi,
        this.toolboxApi,
        codeToolbox,
      )

      if (!params.async) {
        const timeElapsed = Date.now() - startTime;
        await workspace.waitUntilStarted(effectiveTimeout - (timeElapsed / 1000));
      }

      return workspace
    } catch (error) {
      void this.workspaceApi.deleteWorkspace(params.id!, true).catch(() => {});
      if (error instanceof AxiosError && error.message.includes('timeout of') || error instanceof TimeoutError) {
        throw new TimeoutError(`Failed to create and start workspace within ${effectiveTimeout} seconds.`)
      } else {
        throw error
      }
    }
  }

  /**
   * Gets a workspace by its ID
   * @param {string} workspaceId - The ID of the workspace to retrieve
   * @returns {Promise<Workspace>} The workspace instance
   */
  public async get(workspaceId: string): Promise<Workspace> {
    const response = await this.workspaceApi.getWorkspace(workspaceId)
    const workspaceInstance = response.data
    const language = workspaceInstance.labels && workspaceInstance.labels[`code-toolbox-language`]
    const codeToolbox = this.getCodeToolbox(language as CodeLanguage)

    return new Workspace(workspaceId, workspaceInstance, this.workspaceApi, this.toolboxApi, codeToolbox)
  }

  /**
   * Lists all workspaces
   * @returns {Promise<Workspace[]>} The list of workspaces
   */
  public async list(): Promise<Workspace[]> {
    const response = await this.workspaceApi.listWorkspaces()
    return response.data.map((workspace) => {
      const language = workspace.labels?.[`code-toolbox-language`] as CodeLanguage
      if (language && !['python', 'javascript', 'typescript'].includes(language)) {
        throw new Error(`Invalid code-toolbox-language: ${language}`)
      }
      return new Workspace(
        workspace.id, 
        workspace, 
        this.workspaceApi, 
        this.toolboxApi, 
        this.getCodeToolbox(language)
      )
    })
  }

  /**
   * Starts a workspace
   * @param {Workspace} workspace - The workspace to start
   */
  public async start(workspace: Workspace, timeout?: number) {
    await workspace.start(timeout)
  }

  /**
   * Stops a workspace
   * @param {Workspace} workspace - The workspace to stop
   * @returns {Promise<void>}
   */
  public async stop(workspace: Workspace) {
    await workspace.stop()
  }

  /**
   * Removes a workspace
   * @param {Workspace} workspace - The workspace to remove
   * @param {number} timeout - Timeout in seconds (0 means no timeout, default is 60)
   * @returns {Promise<void>}
   */
  public async remove(workspace: Workspace, timeout: number = 60) {
    await this.workspaceApi.deleteWorkspace(workspace.id, true, { timeout: timeout * 1000 })
  }

  /**
   * Gets the current workspace by ID
   * @param {string} workspaceId - The ID of the workspace to retrieve
   * @returns {Promise<Workspace>} The workspace instance
   */
  public async getCurrentWorkspace(workspaceId: string): Promise<Workspace> {
    return this.get(workspaceId)
  }

  private getCodeToolbox(language?: CodeLanguage) {
    switch (language) {
      case 'javascript':
      case 'typescript':
        return new WorkspaceTsCodeToolbox()
      case 'python':
      case undefined:
        return new WorkspacePythonCodeToolbox()
      default:
        throw new Error(`Unsupported language: ${language}`)
    }
  }
}
