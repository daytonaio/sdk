/**
 * The Daytona SDK provides powerful process and code execution capabilities through
 * the `process` module in Sandboxes. This guide covers all available process operations
 * and best practices.
 *
 * @module Process
 *
 * @example
 * // Execute a shell command
 * const response = await sandbox.process.executeCommand('ls -la');
 * console.log(response.result);
 *
 * // Run TypeScript code
 * const response = await sandbox.process.codeRun('console.log("Hello, World!")');
 * console.log(response.result);
 *
 * @example
 * // Using interactive sessions
 * // Create a new session
 * const sessionId = 'my-session';
 * await sandbox.process.createSession(sessionId);
 *
 * // Execute commands in the session
 * const response = await sandbox.process.executeSessionCommand(sessionId, {
 *   command: 'cd /workspace'
 * });
 *
 * const response2 = await sandbox.process.executeSessionCommand(sessionId, {
 *   command: 'pwd'
 * });
 * console.log(response2.result);  // Should print "/workspace"
 *
 * // Clean up
 * await sandbox.process.deleteSession(sessionId);
 */

import { Command, Session, SessionExecuteRequest, SessionExecuteResponse, ToolboxApi } from '@daytonaio/api-client'
import { SandboxCodeToolbox, SandboxInstance } from './Sandbox'
import { ArtifactParser } from './utils/ArtifactParser'
import { ExecuteResponse } from './types/ExecuteResponse'

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

export class Process {
  constructor(
    private readonly codeToolbox: SandboxCodeToolbox,
    private readonly toolboxApi: ToolboxApi,
    private readonly instance: SandboxInstance
  ) {}

  /**
   * Executes a shell command in the Sandbox.
   *
   * @param {string} command - Shell command to execute
   * @param {string} [cwd] - Working directory for command execution. If not specified, uses the Sandbox root directory
   * @param {number} [timeout] - Maximum time in seconds to wait for the command to complete. 0 means wait indefinitely.
   * @returns {Promise<ExecuteResponse>} Command execution results containing:
   *                                    - exitCode: The command's exit status
   *                                    - result: Standard output from the command
   *
   * @example
   * // Simple command
   * const response = await process.executeCommand('echo "Hello"');
   * console.log(response.result);  // Prints: Hello
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
   * @param {string} code - Code to execute
   * @param {CodeRunParams} params - Parameters for code execution
   * @param {number} [timeout] - Maximum time in seconds to wait for execution to complete
   * @returns {Promise<ExecuteResponse>} Code execution results containing:
   *                                    - exitCode: The execution's exit status
   *                                    - result: Standard output from the code
   *
   * @example
   * // Run TypeScript code
   * const response = await process.codeRun(`
   *   const x = 10;
   *   const y = 20;
   *   console.log(\`Sum: \${x + y}\`);
   * `);
   * console.log(response.result);  // Prints: Sum: 30
   *
   * @example
   * // Run Python code with matplotlib
   * const response = await process.codeRun(`
   *   import matplotlib.pyplot as plt
   *   import numpy as np
   *
   *   x = np.linspace(0, 10, 100)
   *   y = np.sin(x)
   *
   *   plt.plot(x, y)
   *   plt.title('Sine Wave')
   *   plt.xlabel('x')
   *   plt.ylabel('sin(x)')
   *   plt.show()
   * `);
   *
   * // Access chart artifacts
   * if (response.artifacts?.charts) {
   *   const chart = response.artifacts.charts[0];
   *   console.log(`Chart title: ${chart.title}`);
   *   console.log(`Chart image: ${chart.png?.substring(0, 20)}...`);
   * }
   */
  public async codeRun(code: string, params?: CodeRunParams, timeout?: number): Promise<ExecuteResponse> {
    const runCommand = this.codeToolbox.getRunCommand(code, params)
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
  public async getSessionCommandLogs(sessionId: string, commandId: string): Promise<string> {
    const response = await this.toolboxApi.getSessionCommandLogs(this.instance.id, sessionId, commandId)
    return response.data
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
}
