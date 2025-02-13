import {
  Command,
  ExecuteResponse,
  Session,
  SessionExecuteRequest,
  SessionExecuteResponse,
  ToolboxApi,
  Workspace,
} from '@daytonaio/api-client'
import { WorkspaceCodeToolbox, WorkspaceInstance } from './Workspace'
import { RawAxiosRequestConfig } from 'axios'

/**
 * Parameters for code execution
 */
export class CodeRunParams {
  /**
   * Command line arguments
   */
  argv?: string[]
  /**
   * Environment variables
   */
  env?: Record<string, string>
}


/**
 * Handles process and code execution within a workspace
 * @class Process
 */
export class Process {
  constructor(
    private readonly codeToolbox: WorkspaceCodeToolbox,
    private readonly toolboxApi: ToolboxApi,
    private readonly instance: WorkspaceInstance,
  ) {}

  /**
   * Executes a shell command in the workspace
   * @param {string} command - Command to execute
   * @returns {Promise<ExecuteResponse>} Command execution results
   */
  public async executeCommand(
    command: string,
    cwd?: string,
    timeout?: number
  ): Promise<ExecuteResponse> {
    const response = await this.toolboxApi.executeCommand(this.instance.id, {
      command,
      timeout,
      cwd,
    })

    return response.data
  }

  /**
   * Executes code in the workspace using the appropriate language runtime
   * @param {string} code - Code to execute
   * @param {CodeRunParams} params - Parameters for code execution
   * @returns {Promise<ExecuteResponse>} Code execution results
   */
  public async codeRun(code: string, params?: CodeRunParams, timeout?: number): Promise<ExecuteResponse> {
    const runCommand = this.codeToolbox.getRunCommand(code, params)

    const response = await this.executeCommand(runCommand, undefined, timeout)

    return response
  }

  /**
   * Creates a new exec session in the workspace
   * @param {string} sessionId - Unique identifier for the session
   * @returns {Promise<ExecuteResponse>} Code execution results
   */
  public async createSession(sessionId: string): Promise<void> {
    await this.toolboxApi.createSession(this.instance.id, {
      sessionId,
    })
  }

  /**
   * Executes a command in the session
   * @param {string} sessionId - Unique identifier for the session
   * @param {SessionExecuteRequest} req - Command to execute and async flag
   * @param {number} timeout - Timeout in seconds
   * @returns {Promise<SessionExecuteResponse>} Command execution results
   */
  public async executeSessionCommand(sessionId: string, req: SessionExecuteRequest, timeout?: number): Promise<SessionExecuteResponse> {
    let options: RawAxiosRequestConfig = {}
    if (timeout) {
      options = { timeout: timeout * 1000 }
    }

    const response = await this.toolboxApi.executeSessionCommand(this.instance.id, sessionId, req, options)
    return response.data
  }

  /**
   * Gets the logs for a command in the session
   * @param {string} sessionId - Unique identifier for the session
   * @param {string} commandId - Unique identifier for the command
   * @returns {Promise<string>} Command logs
   */
  public async getSessionCommandLogs(sessionId: string, commandId: string): Promise<string> {
    const response = await this.toolboxApi.getSessionCommandLogs(this.instance.id, sessionId, commandId)
    return response.data
  }

  /**
   * Gets the session
   * @param {string} sessionId - Unique identifier for the session
   * @returns {Promise<Session>} Session
   */
  public async getSession(sessionId: string): Promise<Session> {
    const response = await this.toolboxApi.getSession(this.instance.id, sessionId)
    return response.data
  }

  /**
   * Gets the session command
   * @param {string} sessionId - Unique identifier for the session
   * @param {string} commandId - Unique identifier for the command
   * @returns {Promise<Command>} Session command
   */
  public async getSessionCommand(sessionId: string, commandId: string): Promise<Command> {
    const response = await this.toolboxApi.getSessionCommand(this.instance.id, sessionId, commandId)
    return response.data
  }

  /**
   * Lists all sessions in the workspace
   * @returns {Promise<Session[]>} List of sessions
   */
  public async listSessions(): Promise<Session[]> {
    const response = await this.toolboxApi.listSessions(this.instance.id)
    return response.data
  }

  /**
   * Deletes a session in the workspace
   * @param {string} sessionId - Unique identifier for the session
   */
  public async deleteSession(sessionId: string): Promise<void> {
    await this.toolboxApi.deleteSession(this.instance.id, sessionId)
  }
}
