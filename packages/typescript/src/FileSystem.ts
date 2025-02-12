import {
  FileInfo,
  Match,
  ReplaceRequest,
  ReplaceResult,
  SearchFilesResponse,
  ToolboxApi,
} from '@daytonaio/api-client'
import { WorkspaceInstance } from './Workspace'

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
    private readonly toolboxApi: ToolboxApi,
  ) {}

  /**
   * Creates a new folder in the workspace
   * @param {string} path - Path where the folder should be created
   * @param {string} mode - Folder permissions in octal format
   * @returns {Promise<void>}
   */
  public async createFolder(path: string, mode: string): Promise<void> {
    const response = await this.toolboxApi.createFolder(this.instance.id, path, mode)
    return response.data
  }

  /**
   * Deletes a file from the workspace
   * @param {string} path - Path to the file to delete
   * @returns {Promise<void>}
   */
  public async deleteFile(path: string): Promise<void> {
    const response = await this.toolboxApi.deleteFile(this.instance.id, path)
    return response.data
  }

  /**
   * Downloads a file from the workspace
   * @param {string} path - Path to the file to download
   * @returns {Promise<Blob>} The file contents as a Blob
   */
  public async downloadFile(path: string): Promise<Blob> {
    const response = await this.toolboxApi.downloadFile(this.instance.id, path)
    return response.data
  }

  /**
   * Searches for files matching a pattern
   * @param {string} path - Directory to search in
   * @param {string} pattern - Search pattern
   * @returns {Promise<Array<Match>>} Array of matching files
   */
  public async findFiles(path: string, pattern: string): Promise<Array<Match>> {
    const response = await this.toolboxApi.findInFiles(this.instance.id, path, pattern)
    return response.data
  }

  /**
   * Gets details about a file
   * @param {string} path - Path to the file
   * @returns {Promise<FileInfo>} File information
   */
  public async getFileDetails(path: string): Promise<FileInfo> {
    const response = await this.toolboxApi.getFileInfo(this.instance.id, path)
    return response.data
  }

  /**
   * Lists files in a directory
   * @param {string} path - Directory path to list
   * @returns {Promise<FileInfo[]>} Array of file information
   */
  public async listFiles(path: string): Promise<FileInfo[]> {
    const response = await this.toolboxApi.listFiles(this.instance.id, path)
    return response.data
  }

  /**
   * Moves/renames files
   * @param {string} source - Source path
   * @param {string} destination - Destination path
   * @returns {Promise<void>}
   */
  public async moveFiles(source: string, destination: string): Promise<void> {
    const response = await this.toolboxApi.moveFile(this.instance.id, source, destination)
    return response.data
  }

  /**
   * Replaces text in multiple files
   * @param {string[]} files - Array of file paths
   * @param {string} pattern - Pattern to replace
   * @param {string} newValue - Replacement value
   * @returns {Promise<Array<ReplaceResult>>} Results of the replace operation
   */
  public async replaceInFiles(
    files: string[],
    pattern: string,
    newValue: string,
  ): Promise<Array<ReplaceResult>> {
    const replaceRequest: ReplaceRequest = {
      files,
      newValue,
      pattern,
    }

    const response = await this.toolboxApi.replaceInFiles(this.instance.id, replaceRequest)
    return response.data
  }

  /**
   * Searches for files by name pattern
   * @param {string} path - Directory to search in
   * @param {string} pattern - Search pattern
   * @returns {Promise<SearchFilesResponse>} Search results
   */
  public async searchFiles(
    path: string,
    pattern: string,
  ): Promise<SearchFilesResponse> {
    const response = await this.toolboxApi.searchFiles(this.instance.id, path, pattern)
    return response.data
  }

  /**
   * Sets file permissions
   * @param {string} path - Path to the file
   * @param {FilePermissionsParams} permissions - Permission settings
   * @returns {Promise<void>}
   */
  public async setFilePermissions(
    path: string,
    permissions: FilePermissionsParams,
  ): Promise<void> {
    const response = await this.toolboxApi.setFilePermissions(this.instance.id, path, permissions.owner!, permissions.group!, permissions.mode!)
    return response.data
  }

  /**
   * Uploads a file to the workspace
   * @param {string} path - Destination path
   * @param {Blob} file - File contents to upload
   * @returns {Promise<void>}
   */
  public async uploadFile(path: string, file: File): Promise<void> {
    const response = await this.toolboxApi.uploadFile(this.instance.id, path, file)
    return response.data
  }
}
