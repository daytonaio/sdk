import {
  ToolboxApi,
  ListBranchResponse,
  GitStatus,
} from '@daytonaio/api-client'
import { Workspace, WorkspaceInstance } from './Workspace'

/**
 * Provides Git operations within a workspace
 * @class Git
 */
export class Git {
  constructor(
    private readonly workspace: Workspace,
    private readonly toolboxApi: ToolboxApi,
    private readonly instance: WorkspaceInstance,
  ) {}

  /**
   * Stages files for commit
   * @param {string} path - Repository path
   * @param {string[]} files - Array of file paths to stage
   * @returns {Promise<void>}
   */
  public async add(path: string, files: string[]): Promise<void> {
    await this.toolboxApi.gitAddFiles(this.instance.id, {
      path,
      files,
    })
  }

  /**
   * Lists branches in the repository
   * @param {string} path - Repository path
   * @returns {Promise<ListBranchResponse>} List of branches
   */
  public async branches(path: string): Promise<ListBranchResponse> {
    const response = await this.toolboxApi.gitListBranches(this.instance.id, path)
    return response.data
  }

  /**
   * Clones a Git repository
   * @param {string} url - Repository URL
   * @param {string} path - Destination path
   * @param {string} [branch] - Branch to clone
   * @param {string} [commitId] - Specific commit to clone
   * @param {string} [username] - Git username for authentication
   * @param {string} [password] - Git password/token for authentication
   * @returns {Promise<void>}
   */
  public async clone(
    url: string,
    path: string,
    branch?: string,
    commitId?: string,
    username?: string,
    password?: string,
  ): Promise<void> {
    await this.toolboxApi.gitCloneRepository(this.instance.id, {
        url: url,
        branch: branch,
        path,
        username,
        password,
        commit_id: commitId
      },
    )
  }

  /**
   * Creates a new commit with staged changes
   * @param {string} path - Repository path
   * @param {string} message - Commit message
   * @param {string} author - Author name
   * @param {string} email - Author email
   * @returns {Promise<void>}
   */
  public async commit(
    path: string,
    message: string,
    author: string,
    email: string,
  ): Promise<void> {
    await this.toolboxApi.gitCommitChanges(this.instance.id, {
      path,
      message,
      author,
      email,
    })
  }

  /**
   * Pushes local commits to remote repository
   * @param {string} path - Repository path
   * @param {string} [username] - Git username for authentication
   * @param {string} [password] - Git password/token for authentication
   * @returns {Promise<void>}
   */
  public async push(
    path: string,
    username?: string,
    password?: string,
  ): Promise<void> {
    await this.toolboxApi.gitPushChanges(this.instance.id, {
      path,
      username,
      password,
    })
  }

  /**
   * Pulls changes from remote repository
   * @param {string} path - Repository path
   * @param {string} [username] - Git username for authentication
   * @param {string} [password] - Git password/token for authentication
   * @returns {Promise<void>}
   */
  public async pull(
    path: string,
    username?: string,
    password?: string,
  ): Promise<void> {
    await this.toolboxApi.gitPullChanges(this.instance.id, {
      path,
      username,
      password,
    })
  }

  /**
   * Gets the current Git repository status
   * @param {string} path - Repository path
   * @returns {Promise<GitStatus>} Repository status information
   */
  public async status(path: string): Promise<GitStatus> {
    const response = await this.toolboxApi.gitGetStatus(this.instance.id, path)
    return response.data
  }
}
