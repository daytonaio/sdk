import { Command, Session, SessionExecuteRequest, SessionExecuteResponse, ToolboxApi } from '@daytonaio/api-client'
import { SandboxInstance } from './Sandbox'
import { ExecuteResponse } from './types/ExecuteResponse'
import { ArtifactParser } from './utils/ArtifactParser'
import { SandboxPythonCodeToolbox } from './code-toolbox/SandboxPythonCodeToolbox'
import { DaytonaError } from './errors/DaytonaError'
import { SandboxTsCodeToolbox } from './code-toolbox/SandboxTsCodeToolbox'

/**
 * Parameters for code execution.
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
 * Supported programming languages for code execution
 */
export enum CodeLanguage {
  PYTHON = 'python',
  TYPESCRIPT = 'typescript',
  JAVASCRIPT = 'javascript',
}

/**
 * Handles process and code execution within a Sandbox.
 *
 * @class
 */
export class Process {
  constructor(private readonly toolboxApi: ToolboxApi, private readonly instance: SandboxInstance) {}

  /**
   * Executes a shell command in the Sandbox.
   *
   * @param {string} command - Shell command to execute
   * @param {string} [cwd] - Working directory for command execution. If not specified, uses the Sandbox root directory
   * @param {number} [timeout] - Maximum time in seconds to wait for the command to complete. 0 means wait indefinitely.
   * @returns {Promise<ExecuteResponse>} Command execution results containing:
   *                                    - exitCode: The command's exit status
   *                                    - result: Standard output from the command
   *                                    - artifacts: ExecutionArtifacts object containing `stdout` (same as result) and `charts` (matplotlib charts metadata)
   *
   * @example
   * // Simple command
   * const response = await process.executeCommand('echo "Hello"');
   * console.log(response.artifacts.stdout);  // Prints: Hello
   *
   * @example
   * // Command with working directory
   * const result = await process.executeCommand('ls', '/workspace/src');
   *
   * @example
   * // Command with timeout
   * const result = await process.executeCommand('sleep 10', undefined, 5);
   */
  public async executeCommand(command: string, cwd?: string, timeout?: number): Promise<ExecuteResponse> {
    const response = await this.toolboxApi.executeCommand(this.instance.id, {
      command,
      timeout,
      cwd,
    })

    // console.log(response)

    // Parse artifacts from the output
    const artifacts = ArtifactParser.parseArtifacts(response.data.result)

    // Return enhanced response with parsed artifacts
    return {
      ...response.data,
      result: artifacts.stdout,
      artifacts,
    }
  }

  /**
   * Executes code in the Sandbox using the appropriate language runtime.
   *
   * @param {"python" | "typescript" | "javascript"} language - Programming language for the code.
   * @param {string} code - Code to execute
   * @param {CodeRunParams} params - Parameters for code execution
   * @param {number} [timeout] - Maximum time in seconds to wait for execution to complete
   * @returns {Promise<ExecuteResponse>} Code execution results containing:
   *                                    - exitCode: The execution's exit status
   *                                    - result: Standard output from the code
   *                                    - artifacts: ExecutionArtifacts object containing `stdout` (same as result) and `charts` (matplotlib charts metadata)
   *
   * @example
   * // Run TypeScript code
   * const response = await sandbox.process.codeRun(
   *   'typescript',
   *   `
   *     const x = 10;
   *     const y = 20;
   *     console.log(\`Sum: \${x + y}\`);
   *   `
   *  );
   * console.log(response.artifacts.stdout);  // Prints: Sum: 30
   *
   * @example
   * // Run Python code with matplotlib
   * const response = await sandbox.process.codeRun(
   *   'python',
   *   `
   * import matplotlib.pyplot as plt
   * import numpy as np
   *
   * x = np.linspace(0, 10, 30)
   * y = np.sin(x)
   *
   * plt.figure(figsize=(8, 5))
   * plt.plot(x, y, 'b-', linewidth=2)
   * plt.title('Line Chart')
   * plt.xlabel('X-axis (seconds)')
   * plt.ylabel('Y-axis (amplitude)')
   * plt.grid(True)
   * plt.show()
   * `
   * );
   *
   * if (response.artifacts?.charts) {
   *   const chart = response.artifacts.charts[0];
   *
   *   console.log(`Type: ${chart.type}`);
   *   console.log(`Title: ${chart.title}`);
   *   if (chart.type === ChartType.LINE) {
   *     const lineChart = chart as LineChart
   *     console.log('X Label:', lineChart.x_label)
   *     console.log('Y Label:', lineChart.y_label)
   *     console.log('X Ticks:', lineChart.x_ticks)
   *     console.log('Y Ticks:', lineChart.y_ticks)
   *     console.log('X Tick Labels:', lineChart.x_tick_labels)
   *     console.log('Y Tick Labels:', lineChart.y_tick_labels)
   *     console.log('X Scale:', lineChart.x_scale)
   *     console.log('Y Scale:', lineChart.y_scale)
   *     console.log('Elements:')
   *     console.dir(lineChart.elements, { depth: null })
   *   }
   * }
   */
  public async codeRun(
    language: 'python' | 'typescript' | 'javascript',
    code: string,
    params?: CodeRunParams,
    timeout?: number
  ): Promise<ExecuteResponse> {
    const runCommand = this.getCodeRunCommand(language as CodeLanguage, code, params)
    return this.executeCommand(runCommand, undefined, timeout)
  }

  /**
   * Creates a new long-running background session in the Sandbox.
   *
   * Sessions are background processes that maintain state between commands, making them ideal for
   * scenarios requiring multiple related commands or persistent environment setup. You can run
   * long-running commands and monitor process status.
   *
   * @param {string} sessionId - Unique identifier for the new session
   * @returns {Promise<void>}
   *
   * @example
   * // Create a new session
   * const sessionId = 'my-session';
   * await process.createSession(sessionId);
   * const session = await process.getSession(sessionId);
   * // Do work...
   * await process.deleteSession(sessionId);
   */
  public async createSession(sessionId: string): Promise<void> {
    await this.toolboxApi.createSession(this.instance.id, {
      sessionId,
    })
  }

  /**
   * Get a session in the sandbox.
   *
   * @param {string} sessionId - Unique identifier of the session to retrieve
   * @returns {Promise<Session>} Session information including:
   *                            - sessionId: The session's unique identifier
   *                            - commands: List of commands executed in the session
   *
   * @example
   * const session = await process.getSession('my-session');
   * session.commands.forEach(cmd => {
   *   console.log(`Command: ${cmd.command}`);
   * });
   */
  public async getSession(sessionId: string): Promise<Session> {
    const response = await this.toolboxApi.getSession(this.instance.id, sessionId)
    return response.data
  }

  /**
   * Gets information about a specific command executed in a session.
   *
   * @param {string} sessionId - Unique identifier of the session
   * @param {string} commandId - Unique identifier of the command
   * @returns {Promise<Command>} Command information including:
   *                            - id: The command's unique identifier
   *                            - command: The executed command string
   *                            - exitCode: Command's exit status (if completed)
   *
   * @example
   * const cmd = await process.getSessionCommand('my-session', 'cmd-123');
   * if (cmd.exitCode === 0) {
   *   console.log(`Command ${cmd.command} completed successfully`);
   * }
   */
  public async getSessionCommand(sessionId: string, commandId: string): Promise<Command> {
    const response = await this.toolboxApi.getSessionCommand(this.instance.id, sessionId, commandId)
    return response.data
  }

  /**
   * Executes a command in an existing session.
   *
   * @param {string} sessionId - Unique identifier of the session to use
   * @param {SessionExecuteRequest} req - Command execution request containing:
   *                                     - command: The command to execute
   *                                     - async: Whether to execute asynchronously
   * @param {number} timeout - Timeout in seconds
   * @returns {Promise<SessionExecuteResponse>} Command execution results containing:
   *                                           - cmdId: Unique identifier for the executed command
   *                                           - output: Command output (if synchronous execution)
   *                                           - exitCode: Command exit status (if synchronous execution)
   *
   * @example
   * // Execute commands in sequence, maintaining state
   * const sessionId = 'my-session';
   *
   * // Change directory
   * await process.executeSessionCommand(sessionId, {
   *   command: 'cd /workspace'
   * });
   *
   * // Run command in new directory
   * const result = await process.executeSessionCommand(sessionId, {
   *   command: 'pwd'
   * });
   * console.log(result.output);  // Prints: /workspace
   */
  public async executeSessionCommand(
    sessionId: string,
    req: SessionExecuteRequest,
    timeout?: number
  ): Promise<SessionExecuteResponse> {
    const response = await this.toolboxApi.executeSessionCommand(
      this.instance.id,
      sessionId,
      req,
      undefined,
      timeout ? { timeout: timeout * 1000 } : {}
    )
    return response.data
  }

  /**
   * Get the logs for a command executed in a session.
   *
   * @param {string} sessionId - Unique identifier of the session
   * @param {string} commandId - Unique identifier of the command
   * @returns {Promise<string>} Command logs
   *
   * @example
   * const logs = await process.getSessionCommandLogs('my-session', 'cmd-123');
   * console.log('Command output:', logs);
   */
  public async getSessionCommandLogs(sessionId: string, commandId: string): Promise<string>
  /**
   * Asynchronously retrieve and process the logs for a command executed in a session as they become available.
   *
   * @param {string} sessionId - Unique identifier of the session
   * @param {string} commandId - Unique identifier of the command
   * @param {function} onLogs - Callback function to handle each log chunk
   * @returns {Promise<void>}
   *
   * @example
   * const logs = await process.getSessionCommandLogs('my-session', 'cmd-123', (chunk) => {
   *   console.log('Log chunk:', chunk);
   * });
   */
  public async getSessionCommandLogs(
    sessionId: string,
    commandId: string,
    onLogs: (chunk: string) => void
  ): Promise<void>
  public async getSessionCommandLogs(
    sessionId: string,
    commandId: string,
    onLogs?: (chunk: string) => void
  ): Promise<string | void> {
    if (!onLogs) {
      const response = await this.toolboxApi.getSessionCommandLogs(this.instance.id, sessionId, commandId)
      return response.data
    }

    await new Promise((resolve, reject) => {
      this.toolboxApi
        .getSessionCommandLogs(this.instance.id, sessionId, commandId, undefined, true, {
          responseType: 'stream',
        })
        .then((res) => {
          const stream = res.data as any

          stream.on('data', (data: Buffer) => {
            const chunk = data.toString('utf-8')
            onLogs(chunk)
          })

          stream.on('close', () => {
            resolve(void 0)
          })

          // TODO: end event is not working
          // stream.on('end', () => {
          //   console.log('stream done - end event')
          //   resolve(void 0)
          // })

          // TODO: error event is triggered at the end of the stream, 'connection aborted'
          // stream.on('error', (err: Error) => {
          //   console.error('Stream error:', err)
          //   reject(err)
          // })
        })
        .catch(reject)
    })
  }

  /**
   * Lists all active sessions in the Sandbox.
   *
   * @returns {Promise<Session[]>} Array of active sessions
   *
   * @example
   * const sessions = await process.listSessions();
   * sessions.forEach(session => {
   *   console.log(`Session ${session.sessionId}:`);
   *   session.commands.forEach(cmd => {
   *     console.log(`- ${cmd.command} (${cmd.exitCode})`);
   *   });
   * });
   */
  public async listSessions(): Promise<Session[]> {
    const response = await this.toolboxApi.listSessions(this.instance.id)
    return response.data
  }

  /**
   * Delete a session from the Sandbox.
   *
   * @param {string} sessionId - Unique identifier of the session to delete
   * @returns {Promise<void>}
   *
   * @example
   * // Clean up a completed session
   * await process.deleteSession('my-session');
   */
  public async deleteSession(sessionId: string): Promise<void> {
    await this.toolboxApi.deleteSession(this.instance.id, sessionId)
  }

  /**
   * Gets the appropriate code toolbox based on language.
   *
   * @private
   * @param {CodeLanguage} [language] - Programming language for the toolbox
   * @param {string} code - Code to execute
   * @param {CodeRunParams} [params] - Parameters for code execution
   * @returns {string} The appropriate code run command
   * @throws {DaytonaError} - `DaytonaError` - When an unsupported language is specified
   */
  private getCodeRunCommand(language: CodeLanguage, code: string, params?: CodeRunParams): string {
    switch (language) {
      case CodeLanguage.JAVASCRIPT:
      case CodeLanguage.TYPESCRIPT:
        return SandboxTsCodeToolbox.getRunCommand(code, params)
      case CodeLanguage.PYTHON:
        return SandboxPythonCodeToolbox.getRunCommand(code, params)
      default:
        throw new DaytonaError(
          `Unsupported language: ${language}, supported languages: ${Object.values(CodeLanguage).join(', ')}`
        )
    }
  }
}
