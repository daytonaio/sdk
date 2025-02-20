/**
 * The Daytona SDK provides comprehensive file system operations through the `fs` module in Sandboxes.
 * You can perform various operations like listing files, creating directories, reading and writing files, and more.
 * This guide covers all available file system operations and best practices.
 * 
 * @module FileSystem
 * 
 * @example
 * // Basic file operations
 * // Create a workspace
 * const workspace = await daytona.create();
 * 
 * // Create a directory
 * await workspace.fs.createFolder('/workspace/data', '755');
 * 
 * // Upload a file
 * const fileContent = new File(['content'], 'local_file.txt');
 * await workspace.fs.uploadFile('/workspace/data/file.txt', fileContent);
 * 
 * // List directory contents
 * const files = await workspace.fs.listFiles('/workspace');
 * files.forEach(file => {
 *   console.log(`Name: ${file.name}`);
 *   console.log(`Is directory: ${file.isDir}`);
 *   console.log(`Size: ${file.size}`);
 *   console.log(`Modified: ${file.modTime}`);
 * });
 * 
 * // Search file contents
 * const matches = await workspace.fs.findFiles(
 *   '/workspace/src',
 *   'text-of-interest'
 * );
 * matches.forEach(match => {
 *   console.log(`Absolute file path: ${match.file}`);
 *   console.log(`Line number: ${match.line}`);
 *   console.log(`Line content: ${match.content}\n`);
 * });
 * 
 * @example
 * // File manipulation
 * // Move files
 * await workspace.fs.moveFiles(
 *   '/workspace/data/old.txt',
 *   '/workspace/data/new.txt'
 * );
 * 
 * // Replace text in files
 * const results = await workspace.fs.replaceInFiles(
 *   ['/workspace/data/new.txt'],
 *   'old_version',
 *   'new_version'
 * );
 * 
 * // Set permissions
 * await workspace.fs.setFilePermissions(
 *   '/workspace/data/script.sh',
 *   {
 *     mode: '755',
 *     owner: 'daytona'
 *   }
 * );
 */

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
 * Parameters for setting file permissions in the Sandbox.
 * 
 * @interface FilePermissionsParams
 * @property {string} [mode] - File mode/permissions in octal format (e.g. "644")
 * @property {string} [owner] - User owner of the file
 * @property {string} [group] - Group owner of the file
 * 
 * @example
 * const permissions: FilePermissionsParams = {
 *   mode: '644',
 *   owner: 'daytona',
 *   group: 'users'
 * };
 */
export type FilePermissionsParams = {
  /** Group owner of the file */
  group?: string
  /** File mode/permissions in octal format (e.g. "644") */
  mode?: string
  /** User owner of the file */
  owner?: string
}

/**
 * Provides file system operations within a Sandbox.
 * 
 * This class implements a high-level interface to file system operations that can
 * be performed within a Daytona Sandbox. It supports common operations like
 * creating, deleting, and moving files, as well as searching file contents and
 * managing permissions.
 */
export class FileSystem {
  constructor(
    private readonly instance: WorkspaceInstance,
    private readonly toolboxApi: ToolboxApi,
  ) {}

  /**
   * Create a new directory in the Sandbox with specified permissions.
   * 
   * @param {string} path - Path where the directory should be created
   * @param {string} mode - Directory permissions in octal format (e.g. "755")
   * @returns {Promise<void>}
   * 
   * @example
   * // Create a directory with standard permissions
   * await fs.createFolder('/app/data', '755');
   */
  public async createFolder(path: string, mode: string): Promise<void> {
    const response = await this.toolboxApi.createFolder(this.instance.id, path, mode)
    return response.data
  }

  /**
   * Deletes a file or directory from the Sandbox.
   * 
   * @param {string} path - Path to the file or directory to delete
   * @returns {Promise<void>}
   * 
   * @example
   * // Delete a file
   * await fs.deleteFile('/app/temp.log');
   */
  public async deleteFile(path: string): Promise<void> {
    const response = await this.toolboxApi.deleteFile(this.instance.id, path)
    return response.data
  }

  /**
   * Downloads a file from the Sandbox.
   * 
   * @param {string} path - Path to the file to download
   * @returns {Promise<Blob>} The file contents as a Blob
   * 
   * @example
   * // Download and process a file
   * const fileBlob = await fs.downloadFile('/app/data.json');
   * console.log('File content:', fileBlob.toString());
   */
  public async downloadFile(path: string): Promise<Blob> {
    const response = await this.toolboxApi.downloadFile(this.instance.id, path)
    return response.data
  }

  /**
   * Searches for text patterns within files in the Sandbox.
   * 
   * @param {string} path - Directory to search in
   * @param {string} pattern - Search pattern
   * @returns {Promise<Array<Match>>} Array of matches with file and line information
   * 
   * @example
   * // Find all TODO comments in TypeScript files
   * const matches = await fs.findFiles('/app/src', 'TODO:');
   * matches.forEach(match => {
   *   console.log(`${match.file}:${match.line}: ${match.content}`);
   * });
   */
  public async findFiles(path: string, pattern: string): Promise<Array<Match>> {
    const response = await this.toolboxApi.findInFiles(this.instance.id, path, pattern)
    return response.data
  }

  /**
   * Retrieves detailed information about a file or directory.
   * 
   * @param {string} path - Path to the file or directory
   * @returns {Promise<FileInfo>} Detailed file information including size, permissions, modification time
   * 
   * @example
   * // Get file details
   * const info = await fs.getFileDetails('/app/config.json');
   * console.log(`Size: ${info.size}, Modified: ${info.modTime}`);
   */
  public async getFileDetails(path: string): Promise<FileInfo> {
    const response = await this.toolboxApi.getFileInfo(this.instance.id, path)
    return response.data
  }

  /**
   * Lists contents of a directory in the Sandbox.
   * 
   * @param {string} path - Directory path to list
   * @returns {Promise<FileInfo[]>} Array of file and directory information
   * 
   * @example
   * // List directory contents
   * const files = await fs.listFiles('/app/src');
   * files.forEach(file => {
   *   console.log(`${file.name} (${file.size} bytes)`);
   * });
   */
  public async listFiles(path: string): Promise<FileInfo[]> {
    const response = await this.toolboxApi.listFiles(this.instance.id, path)
    return response.data
  }

  /**
   * Moves or renames a file or directory.
   * 
   * @param {string} source - Source path
   * @param {string} destination - Destination path
   * @returns {Promise<void>}
   * 
   * @example
   * // Move a file to a new location
   * await fs.moveFiles('/app/temp/data.json', '/app/data/data.json');
   */
  public async moveFiles(source: string, destination: string): Promise<void> {
    const response = await this.toolboxApi.moveFile(this.instance.id, source, destination)
    return response.data
  }

  /**
   * Replaces text content in multiple files.
   * 
   * @param {string[]} files - Array of file paths to process
   * @param {string} pattern - Pattern to replace
   * @param {string} newValue - Replacement text
   * @returns {Promise<Array<ReplaceResult>>} Results of the replace operation for each file
   * 
   * @example
   * // Update version number across multiple files
   * const results = await fs.replaceInFiles(
   *   ['/app/package.json', '/app/version.ts'],
   *   '"version": "1.0.0"',
   *   '"version": "1.1.0"'
   * );
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
   * Searches for files and directories by name pattern in the Sandbox.
   * 
   * @param {string} path - Directory to search in
   * @param {string} pattern - File name pattern (supports globs)
   * @returns {Promise<SearchFilesResponse>} Search results with matching files
   * 
   * @example
   * // Find all TypeScript files
   * const result = await fs.searchFiles('/app', '*.ts');
   * result.files.forEach(file => console.log(file));
   */
  public async searchFiles(
    path: string,
    pattern: string,
  ): Promise<SearchFilesResponse> {
    const response = await this.toolboxApi.searchFiles(this.instance.id, path, pattern)
    return response.data
  }

  /**
   * Sets permissions and ownership for a file or directory.
   * 
   * @param {string} path - Path to the file or directory
   * @param {FilePermissionsParams} permissions - Permission settings
   * @returns {Promise<void>}
   * 
   * @example
   * // Set file permissions and ownership
   * await fs.setFilePermissions('/app/script.sh', {
   *   owner: 'daytona',
   *   group: 'users',
   *   mode: '755'  // Execute permission for shell script
   * });
   */
  public async setFilePermissions(
    path: string,
    permissions: FilePermissionsParams,
  ): Promise<void> {
    const response = await this.toolboxApi.setFilePermissions(this.instance.id, path, permissions.owner!, permissions.group!, permissions.mode!)
    return response.data
  }

  /**
   * Uploads a file to the Sandbox.
   * 
   * @param {string} path - Destination path in the Sandbox
   * @param {File} file - File to upload
   * @returns {Promise<void>}
   * 
   * @example
   * // Upload a configuration file
   * const configFile = new File(['{"setting": "value"}'], 'config.json');
   * await fs.uploadFile('/app/config.json', configFile);
   */
  public async uploadFile(path: string, file: File): Promise<void> {
    const response = await this.toolboxApi.uploadFile(this.instance.id, path, file)
    return response.data
  }
}
