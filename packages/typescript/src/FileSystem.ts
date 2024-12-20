import {
  FileInfo,
  Match,
  ReplaceRequest,
  ReplaceResult,
  SearchFilesResponse,
  Workspace as WorkspaceInstance,
  WorkspaceToolboxApi,
} from './client'

/**
 * Parameters for setting file permissions
 * @interface FilePermissionsParams
 */
type FilePermissionsParams = {
  /** Group owner of the file */
  group?: string
  /** File mode/permissions in octal format (e.g. "644") */
  mode?: string
  /** User owner of the file */
  owner?: string
}

/**
 * Provides file system operations within a workspace
 * @class FileSystem
 */
export class FileSystem {
  constructor(
    private readonly instance: WorkspaceInstance,
    private readonly toolboxApi: WorkspaceToolboxApi,
  ) {}

  /**
   * Creates a new folder in the workspace
   * @param {string} path - Path where the folder should be created
   * @param {string} mode - Folder permissions in octal format
   * @returns {Promise<void>}
   */
  public createFolder(path: string, mode: string): Promise<void> {
    return this.toolboxApi.fsCreateFolder({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      path,
      mode,
    })
  }

  /**
   * Deletes a file from the workspace
   * @param {string} path - Path to the file to delete
   * @returns {Promise<void>}
   */
  public deleteFile(path: string): Promise<void> {
    return this.toolboxApi.fsDeleteFile({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      path,
    })
  }

  /**
   * Downloads a file from the workspace
   * @param {string} path - Path to the file to download
   * @returns {Promise<Blob>} The file contents as a Blob
   */
  public downloadFile(path: string): Promise<Blob> {
    return this.toolboxApi.fsDownloadFile({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      path,
    })
  }

  /**
   * Searches for files matching a pattern
   * @param {string} path - Directory to search in
   * @param {string} pattern - Search pattern
   * @returns {Promise<Array<Match>>} Array of matching files
   */
  public findFiles(path: string, pattern: string): Promise<Array<Match>> {
    return this.toolboxApi.fsFindInFiles({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      path,
      pattern,
    })
  }

  /**
   * Gets details about a file
   * @param {string} path - Path to the file
   * @returns {Promise<FileInfo>} File information
   */
  public getFileDetails(path: string): Promise<FileInfo> {
    return this.toolboxApi.fsGetFileDetails({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      path,
    })
  }

  /**
   * Lists files in a directory
   * @param {string} path - Directory path to list
   * @returns {Promise<FileInfo[]>} Array of file information
   */
  public listFiles(path: string): Promise<FileInfo[]> {
    return this.toolboxApi.fsListFiles({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      path,
    })
  }

  /**
   * Moves/renames files
   * @param {string} source - Source path
   * @param {string} destination - Destination path
   * @returns {Promise<void>}
   */
  public moveFiles(source: string, destination: string): Promise<void> {
    return this.toolboxApi.fsMoveFile({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      source,
      destination,
    })
  }

  /**
   * Replaces text in multiple files
   * @param {string[]} files - Array of file paths
   * @param {string} pattern - Pattern to replace
   * @param {string} newValue - Replacement value
   * @returns {Promise<Array<ReplaceResult>>} Results of the replace operation
   */
  public replaceInFiles(
    files: string[],
    pattern: string,
    newValue: string,
  ): Promise<Array<ReplaceResult>> {
    const ReplaceRequest: ReplaceRequest = {
      files,
      newValue,
      pattern,
    }

    return this.toolboxApi.fsReplaceInFiles({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      replace: ReplaceRequest,
    })
  }

  /**
   * Searches for files by name pattern
   * @param {string} path - Directory to search in
   * @param {string} pattern - Search pattern
   * @returns {Promise<SearchFilesResponse>} Search results
   */
  public searchFiles(
    path: string,
    pattern: string,
  ): Promise<SearchFilesResponse> {
    return this.toolboxApi.fsSearchFiles({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      path,
      pattern,
    })
  }

  /**
   * Sets file permissions
   * @param {string} path - Path to the file
   * @param {FilePermissionsParams} permissions - Permission settings
   * @returns {Promise<void>}
   */
  public setFilePermissions(
    path: string,
    permissions: FilePermissionsParams,
  ): Promise<void> {
    return this.toolboxApi.fsSetFilePermissions({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      path,
      group: permissions.group,
      mode: permissions.mode,
      owner: permissions.owner,
    })
  }

  /**
   * Uploads a file to the workspace
   * @param {string} path - Destination path
   * @param {Blob} file - File contents to upload
   * @returns {Promise<void>}
   */
  public uploadFile(path: string, file: Blob): Promise<void> {
    return this.toolboxApi.fsUploadFile({
      workspaceId: this.instance.id,
      projectId: 'main', //  todo: remove this after project refactor
      path,
      file,
    })
  }
}
