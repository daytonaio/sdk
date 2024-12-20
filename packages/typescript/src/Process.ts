import {
  ExecuteResponse,
  Workspace as WorkspaceInstance,
  WorkspaceToolboxApi,
} from './client'
import { WorkspaceCodeToolbox } from './Workspace'

/**
 * Handles process and code execution within a workspace
 * @class Process
 */
export class Process {
  constructor(
    private readonly codeToolbox: WorkspaceCodeToolbox,
    private readonly toolboxApi: WorkspaceToolboxApi,
    private readonly instance: WorkspaceInstance,
  ) {}

  /**
   * Executes a shell command in the workspace
   * @param {string} command - Command to execute
   * @returns {Promise<ExecuteResponse>} Command execution results
   */
  public async processExecuteCommand(
    command: string,
  ): Promise<ExecuteResponse> {
    return this.toolboxApi.processExecuteCommand({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      params: {
        command,
      },
    })
  }

  /**
   * Executes code in the workspace using the appropriate language runtime
   * @param {string} code - Code to execute
   * @returns {Promise<ExecuteResponse>} Code execution results
   */
  public codeRun(code: string): Promise<ExecuteResponse> {
    const runCommand = this.codeToolbox.getRunCommand(code)

    return this.toolboxApi.processExecuteCommand({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      params: {
        command: runCommand,
      },
    })
  }
}
