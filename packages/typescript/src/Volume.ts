import { ToolboxApi, VolumeDto, VolumesApi } from '@daytonaio/api-client'
import { SandboxInstance } from './Sandbox'

/**
 * Represents a Daytona Volume which is a shared storage volume for Sandboxes.
 *
 * @property {string} id - Unique identifier for the Volume
 * @property {string} name - Name of the Volume
 * @property {string} organizationId - Organization ID that owns the Volume
 * @property {string} state - Current state of the Volume
 * @property {string} createdAt - Date and time when the Volume was created
 * @property {string} updatedAt - Date and time when the Volume was last updated
 * @property {string} lastUsedAt - Date and time when the Volume was last used
 */
export type Volume = VolumeDto & { __brand: 'Volume' }

/**
 * Service for managing Daytona Volumes.
 *
 * This service provides methods to list, get, create, and delete Volumes.
 *
 * @class
 */
export class VolumeService {
  constructor(private volumesApi: VolumesApi) {}

  /**
   * Lists all available Volumes.
   *
   * @returns {Promise<Volume[]>} List of all Volumes accessible to the user
   *
   * @example
   * const daytona = new Daytona();
   * const volumes = await daytona.volume.list();
   * console.log(`Found ${volumes.length} volumes`);
   * volumes.forEach(vol => console.log(`${vol.name} (${vol.id})`));
   */
  async list(): Promise<Volume[]> {
    const response = await this.volumesApi.listVolumes()
    return response.data as Volume[]
  }

  /**
   * Gets a Volume by its ID.
   *
   * @param {string} id - ID of the Volume to retrieve
   * @returns {Promise<Volume>} The requested Volume
   * @throws {Error} If the Volume does not exist or cannot be accessed
   *
   * @example
   * const daytona = new Daytona();
   * const volume = await daytona.volume.get("volume-uuid");
   * console.log(`Volume ${volume.name} is in state ${volume.state}`);
   */
  // TODO: volume - should be name
  async get(id: string): Promise<Volume> {
    const response = await this.volumesApi.getVolume(id)
    return response.data as Volume
  }

  /**
   * Creates a new Volume with the specified name.
   *
   * @param {string} name - Name for the new Volume
   * @returns {Promise<Volume>} The newly created Volume
   * @throws {Error} If the Volume cannot be created
   *
   * @example
   * const daytona = new Daytona();
   * const volume = await daytona.volume.create("my-data-volume");
   * console.log(`Created volume ${volume.name} with ID ${volume.id}`);
   */
  async create(name: string): Promise<Volume> {
    const response = await this.volumesApi.createVolume({ name })
    return response.data as Volume
  }

  /**
   * Deletes a Volume by its ID.
   *
   * @param {string} id - ID of the Volume to delete
   * @returns {Promise<void>}
   * @throws {Error} If the Volume does not exist or cannot be deleted
   *
   * @example
   * const daytona = new Daytona();
   * await daytona.volume.delete("volume-uuid");
   * console.log("Volume deleted successfully");
   */
  // TODO: volume - should be name
  async delete(id: string): Promise<void> {
    await this.volumesApi.deleteVolume(id)
  }
}

/**
 * Service for managing Volume operations within a Sandbox.
 *
 * This service provides methods to mount and unmount Volumes to specific paths
 * within a Sandbox's filesystem.
 *
 * @class
 */
export class SandboxVolumeService {
  constructor(private instance: SandboxInstance, private toolboxApi: ToolboxApi) {}

  /**
   * Mounts a Volume to a specific path in the Sandbox.
   *
   * This makes the Volume's contents available at the specified path
   * in the Sandbox's filesystem.
   *
   * @param {string} volumeId - ID of the Volume to mount
   * @param {string} path - Path in the Sandbox where the Volume should be mounted
   * @returns {Promise<void>}
   * @throws {Error} If the Volume cannot be mounted
   *
   * @example
   * const daytona = new Daytona();
   * const sandbox = await daytona.create();
   * await sandbox.volume.mount("volume-uuid", "/mnt/data");
   */
  // TODO: volume - should be volume name
  async mount(volumeId: string, path: string): Promise<void> {
    await this.toolboxApi.mountVolume(this.instance.id, { volumeId, path })
  }

  /**
   * Unmounts a Volume from the Sandbox.
   *
   * This removes the Volume from the Sandbox's filesystem.
   * Any data written to the Volume while mounted will be preserved.
   *
   * @param {string} volumeId - ID of the Volume to unmount
   * @returns {Promise<void>}
   * @throws {Error} If the Volume cannot be unmounted
   *
   * @example
   * const daytona = new Daytona();
   * const sandbox = await daytona.create();
   *
   * // Mount volume
   * await sandbox.volume.mount("volume-uuid", "/mnt/data");
   * // Use volume
   * await sandbox.process.exec("echo 'hello' > /mnt/data/test.txt");
   * // Unmount when done
   * await sandbox.volume.unmount("volume-uuid");
   * console.log(`Volume ${volume.name} unmounted`);
   */
  // TODO: volume - should be volume name
  async unmount(volumeId: string): Promise<void> {
    await this.toolboxApi.unmountVolume(this.instance.id, { volumeId, path: '/' })
  }
}
