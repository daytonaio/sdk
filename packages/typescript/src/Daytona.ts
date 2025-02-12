import { v4 as uuidv4 } from 'uuid'

import { WorkspacePythonCodeToolbox } from './code-toolbox/WorkspacePythonCodeToolbox'
import { Workspace, WorkspaceInstance } from './Workspace'
import {
  Configuration,
  WorkspaceApi,
  ToolboxApi,
  CreateWorkspaceTargetEnum as WorkspaceTargetRegion
} from '@daytonaio/api-client'
import { WorkspaceTsCodeToolbox } from './code-toolbox/WorkspaceTsCodeToolbox'
import axios from 'axios'
import { DaytonaError } from './errors/DaytonaError'

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
  target: WorkspaceTargetRegion
}

/**
 * Supported programming languages for code execution
 */
export enum CodeLanguage {
    PYTHON = "python",
    TYPESCRIPT = "typescript",
    JAVASCRIPT = "javascript",
}

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
  language?: CodeLanguage | string
  /** Optional environment variables to set in the workspace */
  envVars?: Record<string, string>
  /** Workspace labels */
  labels?: Record<string, string>
  /** Is the workspace port preview public */
  public?: boolean
  /** Target location for the workspace */
  target?: WorkspaceTargetRegion | string
  /** Resource allocation for the workspace */
  resources?: WorkspaceResources
  /** If true, will not wait for the workspace to be ready before returning */
  async?: boolean
  /** Timeout in seconds, for the workspace to be ready (0 means no timeout) */
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
  private readonly target: WorkspaceTargetRegion

  private readonly apiKey: string
  private readonly serverUrl: string

  /**
   * Creates a new Daytona client instance
   * @param {DaytonaConfig} [config] - Configuration options
   * @throws {DaytonaError} When API key or server URL is missing
   */
  constructor(config?: DaytonaConfig) {
    const apiKey = config?.apiKey || process.env.DAYTONA_API_KEY
    if (!apiKey) {
      throw new DaytonaError('API key is required')
    }
    const serverUrl = config?.serverUrl || process.env.DAYTONA_SERVER_URL
    if (!serverUrl) {
      throw new DaytonaError('Server URL is required')
    }
    const envTarget = process.env.DAYTONA_TARGET as WorkspaceTargetRegion
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

    const axiosInstance = axios.create();
    axiosInstance.interceptors.response.use(
      (response) => {
        return response
      },
      (error) => {
        const errorMessage =
          error.response?.data?.message ||
          error.response?.data ||
          error.message ||
          String(error);

        throw new DaytonaError(errorMessage);
      }
    )

    this.workspaceApi = new WorkspaceApi(configuration, '', axiosInstance)
    this.toolboxApi = new ToolboxApi(configuration, '', axiosInstance)
  }

  /**
   * Creates a new workspace
   * @param {CreateWorkspaceParams} [params] - Parameters for workspace creation
   * @returns {Promise<Workspace>} The created workspace instance
   */
  public async create(params?: CreateWorkspaceParams): Promise<Workspace> {
    if (params?.autoStopInterval !== undefined && (!Number.isInteger(params.autoStopInterval) || params.autoStopInterval < 0)) {
      throw new DaytonaError('autoStopInterval must be a non-negative integer');
    }

    const workspaceId = params?.id || `sandbox-${uuidv4().slice(0, 8)}`

    const codeToolbox = this.getCodeToolbox(params?.language as CodeLanguage)

    const labels = params?.labels || {}
    if (params?.language) {
      labels[`code-toolbox-language`] = params.language
    }

    if (params?.timeout && params.timeout < 0) {
      throw new DaytonaError('Timeout must be a non-negative number')
    }

    const response = await this.workspaceApi.createWorkspace({
        id: workspaceId,
        name: workspaceId, //  todo: remove this after project refactor
        image: params?.image,
        user: params?.user,
        env: params?.envVars || {},
        target: this.target,
        cpu: params?.resources?.cpu,
        gpu: params?.resources?.gpu,
        memory: params?.resources?.memory,
        disk: params?.resources?.disk,
        autoStopInterval: params?.autoStopInterval,
    })

    const workspaceInstance = response.data
    const workspaceInfo = Workspace.toWorkspaceInfo(workspaceInstance)
    workspaceInstance.info = workspaceInfo

    const workspace = new Workspace(
      workspaceId,
      workspaceInstance as WorkspaceInstance,
      this.workspaceApi,
      this.toolboxApi,
      codeToolbox,
    )

    if (!params?.async) {
      await workspace.waitUntilStarted(params?.timeout)
    }

    return workspace
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
    const workspaceInfo = Workspace.toWorkspaceInfo(workspaceInstance)
    workspaceInstance.info = workspaceInfo

    return new Workspace(workspaceId, workspaceInstance as WorkspaceInstance, this.workspaceApi, this.toolboxApi, codeToolbox)
  }

  /**
   * Lists all workspaces
   * @returns {Promise<Workspace[]>} The list of workspaces
   */
  public async list(): Promise<Workspace[]> {
    const response = await this.workspaceApi.listWorkspaces()
    return response.data.map((workspace) => {
      const language = workspace.labels?.[`code-toolbox-language`] as CodeLanguage
      const workspaceInfo = Workspace.toWorkspaceInfo(workspace)
      workspace.info = workspaceInfo

      return new Workspace(
        workspace.id, 
        workspace as WorkspaceInstance, 
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
   * @returns {Promise<void>}
   */
  public async remove(workspace: Workspace) {
    await this.workspaceApi.deleteWorkspace(workspace.id, true)
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
      case CodeLanguage.JAVASCRIPT:
      case CodeLanguage.TYPESCRIPT:
        return new WorkspaceTsCodeToolbox()
      case CodeLanguage.PYTHON:
      case undefined:
        return new WorkspacePythonCodeToolbox()
      default:
        throw new DaytonaError(`Unsupported language: ${language}, supported languages: ${Object.values(CodeLanguage).join(', ')}`)
    }
  }
}
