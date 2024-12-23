import { v4 as uuidv4 } from 'uuid'

import { WorkspacePythonCodeToolbox } from './code-toolbox/WorkspacePythonCodeToolbox'
import { Workspace } from './Workspace'
import {
  Configuration,
  WorkspaceApi,
  GitProviderApi,
  WorkspaceToolboxApi,
  CreateProjectDTO,
} from './client'
import { WorkspaceTsCodeToolbox } from './code-toolbox/WorkspaceTsCodeToolbox'

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
  target: string
}

/** 
 * Supported programming languages for code execution
 * @typedef {('python'|'javascript'|'typescript')} CodeLanguage
 */
export type CodeLanguage = 'python' | 'javascript' | 'typescript'

/**
 * Parameters for creating a new workspace
 * @interface CreateWorkspaceParams
 */
export type CreateWorkspaceParams = {
  /** Optional workspace ID. If not provided, a random ID will be generated */
  id?: string
  /** Optional Docker image to use for the workspace */
  image?: string
  /** Programming language to use in the workspace */
  language: CodeLanguage
}

/**
 * Main class for interacting with Daytona Server API
 * @class Daytona
 */
export class Daytona {
  private readonly gitProviderApi: GitProviderApi
  private readonly workspaceApi: WorkspaceApi
  private readonly toolboxApi: WorkspaceToolboxApi
  private readonly target: string

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
    const target = config?.target || process.env.DAYTONA_TARGET || 'local'

    this.apiKey = apiKey
    this.serverUrl = serverUrl
    this.target = target

    const configuration = new Configuration({
      basePath: this.serverUrl,
      //  apiKey: this.apiKey,
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
      },
    })

    this.gitProviderApi = new GitProviderApi(configuration)
    this.workspaceApi = new WorkspaceApi(configuration)
    this.toolboxApi = new WorkspaceToolboxApi(configuration)
  }

  /**
   * Creates a new workspace
   * @param {CreateWorkspaceParams} [params] - Parameters for workspace creation
   * @returns {Promise<Workspace>} The created workspace instance
   */
  public async create(params?: CreateWorkspaceParams): Promise<Workspace> {
    const workspaceId = params?.id || `sandbox-${uuidv4().slice(0, 8)}`

    const codeToolbox = (() => {
      if (!params) {
        //  use python as default language
        return new WorkspacePythonCodeToolbox()
      }
      switch (params?.language) {
        case 'javascript':
        case 'typescript':
          return new WorkspaceTsCodeToolbox()
        case 'python':
          return new WorkspacePythonCodeToolbox()
        default:
          throw new Error(`Unsupported language: ${params?.language}`)
      }
    })()

    const projects: CreateProjectDTO[] = [
      {
        name: 'main',
        image: params?.image || codeToolbox.getDefaultImage(),
        envVars: {
          DAYTONA_SKIP_CLONE: 'true',
        },
        source: {
          //  todo: remove when repo is not required
          repository: {
            branch: 'main',
            cloneTarget: 'branch',
            id: 'python-helloworld',
            name: 'python-helloworld',
            owner: 'dbarnett',
            path: undefined,
            prNumber: undefined,
            sha: '288d7ced1b971fd1b3b0c36002b96e1c3f91542e',
            source: 'github.com',
            url: 'https://github.com/dbarnett/python-helloworld.git',
          },
        },
      },
    ]

    const workspaceInstance = await this.workspaceApi.createWorkspace({
      workspace: {
        id: workspaceId,
        name: workspaceId, //  todo: remove this after project refactor
        projects,
        target: this.target,
      },
    })

    const workspace = new Workspace(
      workspaceId,
      workspaceInstance,
      this.toolboxApi,
      codeToolbox,
    )

    return workspace
  }

  /**
   * Removes a workspace
   * @param {Workspace} workspace - The workspace to remove
   * @returns {Promise<void>}
   */
  public remove(workspace: Workspace) {
    return this.workspaceApi.removeWorkspace({
      workspaceId: workspace.id,
    })
  }
}
