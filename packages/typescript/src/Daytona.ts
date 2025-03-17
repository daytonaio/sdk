/**
 * Sandboxes are isolated development environments managed by Daytona.
 * This guide covers how to create, manage, and remove Sandboxes using the SDK.
 * 
 * @module Daytona
 * 
 * @example
 * // Initialize using environment variables (DAYTONA_API_KEY, DAYTONA_SERVER_URL, DAYTONA_TARGET)
 * const daytona = new Daytona();
 * 
 * // Create and use a sandbox
 * const sandbox = await daytona.create({
 *     language: 'typescript',
 *     envVars: { NODE_ENV: 'development' }
 * });
 * 
 * // Execute commands in the sandbox
 * const response = await sandbox.process.executeCommand('echo "Hello, World!"');
 * console.log(response.result);
 * 
 * // Execute code in the sandbox
 * const response = await sandbox.process.codeRun('console.log("Hello, World!")');
 * console.log(response.result);
 * 
 * @example
 * // Initialize with explicit configuration
 * const daytona = new Daytona({
 *     apiKey: process.env.CUSTOM_API_KEY,
 *     serverUrl: 'https://daytona.example.com',
 *     target: 'us'
 * });
 * 
 * // Create a custom sandbox
 * const sandbox = await daytona.create({
 *     language: 'typescript',
 *     image: 'node:18',
 *     resources: {
 *         cpu: 2,
 *         memory: 4 // 4GB RAM
 *     },
 *     autoStopInterval: 60 // Auto-stop after 1 hour of inactivity
 * });
 * 
 * // Use sandbox features
 * await sandbox.git.clone('https://github.com/user/repo.git');
 * await sandbox.process.executeCommand('npm test');
 */

import { SandboxPythonCodeToolbox } from './code-toolbox/SandboxPythonCodeToolbox'
import { Sandbox, SandboxInstance, Sandbox as Workspace } from './Sandbox'
import {
  Configuration,
  WorkspaceApi as SandboxApi,
  ToolboxApi,
  CreateWorkspaceTargetEnum as SandboxTargetRegion
} from '@daytonaio/api-client'
import { SandboxTsCodeToolbox } from './code-toolbox/SandboxTsCodeToolbox'
import axios, { AxiosError } from 'axios'
import { DaytonaError } from './errors/DaytonaError'

/**
 * Configuration options for initializing the Daytona client.
 * 
 * @interface
 * @property {string} apiKey - API key for authentication with Daytona server
 * @property {string} serverUrl - URL of the Daytona server
 * @property {CreateSandboxTargetEnum} target - Target location for Sandboxes
 * 
 * @example
 * const config: DaytonaConfig = {
 *     apiKey: "your-api-key",
 *     serverUrl: "https://your-server.com",
 *     target: "us"
 * };
 * const daytona = new Daytona(config);
 */
export interface DaytonaConfig {
  /** API key for authentication with Daytona server */
  apiKey: string
  /** URL of the Daytona server */
  serverUrl: string
  /** Target environment for sandboxes */
  target: SandboxTargetRegion
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
 * Resource allocation for a Sandbox.
 * 
 * @interface
 * @property {number} [cpu] - CPU allocation for the Sandbox in cores
 * @property {number} [gpu] - GPU allocation for the Sandbox in units
 * @property {number} [memory] - Memory allocation for the Sandbox in GB
 * @property {number} [disk] - Disk space allocation for the Sandbox in GB
 * 
 * @example
 * const resources: SandboxResources = {
 *     cpu: 2,
 *     memory: 4,  // 4GB RAM
 *     disk: 20    // 20GB disk
 * };
 */
export interface SandboxResources {
  /** CPU allocation for the Sandbox */
  cpu?: number
  /** GPU allocation for the Sandbox */
  gpu?: number
  /** Memory allocation for the Sandbox in GB */
  memory?: number
  /** Disk space allocation for the Sandbox in GB */
  disk?: number
}

/**
 * Parameters for creating a new Sandbox.
 * 
 * @interface
 * @property {string} [id] - Optional Sandbox ID. If not provided, a random ID will be generated
 * @property {string} [image] - Optional Docker image to use for the Sandbox
 * @property {string} [user] - Optional os user to use for the Sandbox
 * @property {CodeLanguage} [language] - Programming language for direct code execution
 * @property {Record<string, string>} [envVars] - Optional environment variables to set in the Sandbox
 * @property {Record<string, string>} [labels] - Sandbox labels
 * @property {boolean} [public] - Is the Sandbox port preview public
 * @property {string} [target] - Target location for the Sandbox
 * @property {SandboxResources} [resources] - Resource allocation for the Sandbox
 * @property {boolean} [async] - If true, will not wait for the Sandbox to be ready before returning
 * @property {number} [timeout] - Timeout in seconds for the Sandbox to be ready (0 means no timeout)
 * @property {number} [autoStopInterval] - Auto-stop interval in minutes (0 means disabled)
 * 
 * @example
 * const params: CreateSandboxParams = {
 *     language: 'typescript',
 *     envVars: { NODE_ENV: 'development' },
 *     resources: {
 *         cpu: 2,
 *         memory: 4 // 4GB RAM
 *     },
 *     autoStopInterval: 60  // Auto-stop after 1 hour of inactivity
 * };
 * const sandbox = await daytona.create(params, 50);
 */
export type CreateSandboxParams = {
  /** Optional Sandbox ID. If not provided, a random ID will be generated */
  id?: string
  /** Optional Docker image to use for the Sandbox */
  image?: string
  /** Optional os user to use for the Sandbox */
  user?: string
  /** Programming language for direct code execution */
  language?: CodeLanguage | string
  /** Optional environment variables to set in the sandbox */
  envVars?: Record<string, string>
  /** Sandbox labels */
  labels?: Record<string, string>
  /** Is the Sandbox port preview public */
  public?: boolean
  /** Target location for the Sandbox */
  target?: SandboxTargetRegion | string
  /** Resource allocation for the Sandbox */
  resources?: SandboxResources
  /** If true, will not wait for the Sandbox to be ready before returning */
  async?: boolean
  /**
   * Timeout in seconds, for the Sandbox to be ready (0 means no timeout)
   * @deprecated Use methods with `timeout` parameter instead
   */
  timeout?: number
  /** Auto-stop interval in minutes (0 means disabled) (must be a non-negative integer) */
  autoStopInterval?: number
}

/**
 * Main class for interacting with Daytona Server API.
 * 
 * Provides methods for creating, managing, and interacting with Daytona Sandboxes.
 * Can be initialized either with explicit configuration or using environment variables.
 * 
 * 
 * @example 
 * // Using environment variables
 * // Uses DAYTONA_API_KEY, DAYTONA_SERVER_URL, DAYTONA_TARGET
 * const daytona = new Daytona();
 * const sandbox = await daytona.create();
 * 
 * @example 
 * // Using explicit configuration
 * const config: DaytonaConfig = {
 *     apiKey: "your-api-key",
 *     serverUrl: "https://your-server.com",
 *     target: "us"
 * };
 * const daytona = new Daytona(config);
 * 
 * @class
 */
export class Daytona {
  private readonly sandboxApi: SandboxApi
  private readonly toolboxApi: ToolboxApi
  private readonly target: SandboxTargetRegion
  private readonly apiKey: string
  private readonly serverUrl: string

  /**
   * Creates a new Daytona client instance.
   * 
   * @param {DaytonaConfig} [config] - Configuration options
   * @throws {DaytonaError} - `DaytonaError` - When API key or server URL is missing
   */
  constructor(config?: DaytonaConfig) {
    const apiKey = config?.apiKey || process.env.DAYTONA_API_KEY
    if (!apiKey) {
      throw new DaytonaError('API key is required')
    }
    const serverUrl = config?.serverUrl || process.env.DAYTONA_SERVER_URL || 'https://app.daytona.io/api'
    const envTarget = process.env.DAYTONA_TARGET as SandboxTargetRegion
    const target = config?.target || envTarget || SandboxTargetRegion.US

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
        let errorMessage: string;

        if (error instanceof AxiosError && error.message.includes('timeout of')) {
          errorMessage = "Operation timed out"
        } else {
          errorMessage =
            error.response?.data?.message ||
            error.response?.data ||
            error.message ||
            String(error);
        }

        throw new DaytonaError(errorMessage);
      }
    )

    this.sandboxApi = new SandboxApi(configuration, '', axiosInstance)
    this.toolboxApi = new ToolboxApi(configuration, '', axiosInstance)
  }

  /**
   * Creates Sandboxes with default or custom configurations. You can specify various parameters,
   * including language, image, resources, environment variables, and volumes for the Sandbox.
   * 
   * @param {CreateSandboxParams} [params] - Parameters for Sandbox creation
   * @param {number} [timeout] - Timeout in seconds (0 means no timeout, default is 60)
   * @returns {Promise<Sandbox>} The created Sandbox instance
   * 
   * @example
   * // Create a default sandbox
   * const sandbox = await daytona.create();
   * 
   * @example
   * // Create a custom sandbox
   * const params: CreateSandboxParams = {
   *     language: 'typescript',
   *     image: 'node:18',
   *     envVars: { 
   *         NODE_ENV: 'development',
   *         DEBUG: 'true'
   *     },
   *     resources: {
   *         cpu: 2,
   *         memory: 4 // 4GB RAM
   *     },
   *     autoStopInterval: 60
   * };
   * const sandbox = await daytona.create(params, 40);
   */
  public async create(params?: CreateSandboxParams, timeout: number = 60): Promise<Sandbox> {
    // const startTime = Date.now();

    if (params == null) {
      params = { language: 'python' }
    }

    const labels = params.labels || {}
    if (params.language) {
      labels[`code-toolbox-language`] = params.language
    }

    // remove this when params.timeout is removed
    const effectiveTimeout = params.timeout || timeout
    if (effectiveTimeout < 0) {
      throw new DaytonaError('Timeout must be a non-negative number')
    }

    if (params.autoStopInterval !== undefined && (!Number.isInteger(params.autoStopInterval) || params.autoStopInterval < 0)) {
      throw new DaytonaError('autoStopInterval must be a non-negative integer');
    }

    const codeToolbox = this.getCodeToolbox(params.language as CodeLanguage)

    try {
      const response = await this.sandboxApi.createWorkspace({
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

      const sandboxInstance = response.data
      const sandboxInfo = Sandbox.toSandboxInfo(sandboxInstance)
      sandboxInstance.info = sandboxInfo

      const sandbox = new Sandbox(
        sandboxInstance.id!,
        sandboxInstance as SandboxInstance,
        this.sandboxApi,
        this.toolboxApi,
        codeToolbox,
      )

      // if (!params.async) {
      //   const timeElapsed = Date.now() - startTime;
      //   await sandbox.waitUntilStarted(effectiveTimeout ? effectiveTimeout - (timeElapsed / 1000) : 0);
      // }

      return sandbox
    } catch (error) {
      void this.sandboxApi.deleteWorkspace(params.id!, true).catch(() => {});
      if (error instanceof DaytonaError && error.message.includes("Operation timed out")) {
        throw new DaytonaError(`Failed to create and start sandbox within ${effectiveTimeout} seconds. Operation timed out.`)
      }
      throw error
    }
  }

  /**
   * Gets a Sandbox by its ID.
   * 
   * @param {string} sandboxId - The ID of the Sandbox to retrieve
   * @returns {Promise<Sandbox>} The Sandbox
   * 
   * @example
   * const sandbox = await daytona.get('my-sandbox-id');
   * console.log(`Sandbox state: ${sandbox.instance.state}`);
   */
  public async get(sandboxId: string): Promise<Sandbox> {
    const response = await this.sandboxApi.getWorkspace(sandboxId)
    const sandboxInstance = response.data
    const language = sandboxInstance.labels && sandboxInstance.labels[`code-toolbox-language`]
    const codeToolbox = this.getCodeToolbox(language as CodeLanguage)
    const sandboxInfo = Sandbox.toSandboxInfo(sandboxInstance)
    sandboxInstance.info = sandboxInfo

    return new Sandbox(sandboxId, sandboxInstance as SandboxInstance, this.sandboxApi, this.toolboxApi, codeToolbox)
  }

  /**
   * Lists all Sandboxes.
   * 
   * @returns {Promise<Sandbox[]>} Array of Sandboxes
   * 
   * @example
   * const sandboxes = await daytona.list();
   * for (const sandbox of sandboxes) {
   *     console.log(`${sandbox.id}: ${sandbox.instance.state}`);
   * }
   */
  public async list(): Promise<Sandbox[]> {
    const response = await this.sandboxApi.listWorkspaces()
    return response.data.map((sandbox) => {
      const language = sandbox.labels?.[`code-toolbox-language`] as CodeLanguage
      const sandboxInfo = Sandbox.toSandboxInfo(sandbox)
      sandbox.info = sandboxInfo

      return new Sandbox(
        sandbox.id, 
        sandbox as SandboxInstance, 
        this.sandboxApi, 
        this.toolboxApi, 
        this.getCodeToolbox(language)
      )
    })
  }

  /**
   * Starts a Sandbox and waits for it to be ready.
   * 
   * @param {Sandbox} sandbox - The Sandbox to start
   * @param {number} [timeout] - Optional timeout in seconds (0 means no timeout)
   * @returns {Promise<void>}
   * 
   * @example
   * const sandbox = await daytona.get('my-sandbox-id');
   * // Wait up to 60 seconds for the sandbox to start
   * await daytona.start(sandbox, 60);
   */
  public async start(sandbox: Sandbox, timeout?: number) {
    await sandbox.start(timeout)
  }

  /**
   * Stops a Sandbox.
   * 
   * @param {Sandbox} sandbox - The Sandbox to stop
   * @returns {Promise<void>}
   * 
   * @example
   * const sandbox = await daytona.get('my-sandbox-id');
   * await daytona.stop(sandbox);
   */
  public async stop(sandbox: Sandbox) {
    await sandbox.stop()
  }

  /**
   * Removes a Sandbox.
   * 
   * @param {Sandbox} sandbox - The Sandbox to remove
   * @param {number} timeout - Timeout in seconds (0 means no timeout, default is 60)
   * @returns {Promise<void>}
   * 
   * @example
   * const sandbox = await daytona.get('my-sandbox-id');
   * await daytona.remove(sandbox);
   */
  public async remove(sandbox: Sandbox, timeout: number = 60) {
    await this.sandboxApi.deleteWorkspace(sandbox.id, true, { timeout: timeout * 1000 })
  }

  /**
   * Gets the Sandbox by ID.
   * 
   * @param {string} workspaceId - The ID of the Sandbox to retrieve
   * @returns {Promise<Workspace>} The Sandbox
   * 
   * @deprecated Use `getCurrentSandbox` instead. This method will be removed in a future version.
   */
  public async getCurrentWorkspace(workspaceId: string): Promise<Workspace> {
    return await this.getCurrentSandbox(workspaceId)
  }

  /**
   * Gets the Sandbox by ID.
   * 
   * @param {string} sandboxId - The ID of the Sandbox to retrieve
   * @returns {Promise<Sandbox>} The Sandbox
   * 
   * @example
   * const sandbox = await daytona.getCurrentSandbox('my-sandbox-id');
   * console.log(`Current sandbox state: ${sandbox.instance.state}`);
   */
  public async getCurrentSandbox(sandboxId: string): Promise<Sandbox> {
    return await this.get(sandboxId)
  }

  /**
   * Gets the appropriate code toolbox based on language.
   * 
   * @private
   * @param {CodeLanguage} [language] - Programming language for the toolbox
   * @returns {SandboxCodeToolbox} The appropriate code toolbox instance
   * @throws {DaytonaError} - `DaytonaError` - When an unsupported language is specified
   */
  private getCodeToolbox(language?: CodeLanguage) {
    switch (language) {
      case CodeLanguage.JAVASCRIPT:
      case CodeLanguage.TYPESCRIPT:
        return new SandboxTsCodeToolbox()
      case CodeLanguage.PYTHON:
      case undefined:
        return new SandboxPythonCodeToolbox()
      default:
        throw new DaytonaError(`Unsupported language: ${language}, supported languages: ${Object.values(CodeLanguage).join(', ')}`)
    }
  }
}
