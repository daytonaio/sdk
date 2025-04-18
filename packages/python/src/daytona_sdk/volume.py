from typing import List

from daytona_api_client import (
    CreateVolume,
    ToolboxApi,
    VolumeDto,
    VolumeMountDto,
    VolumesApi,
)

from .protocols import SandboxInstance


class Volume(VolumeDto):
    """Represents a Daytona Volume which is a shared storage volume for Sandboxes.

    Attributes:
        id (StrictStr): Unique identifier for the Volume.
        name (StrictStr): Name of the Volume.
        organization_id (StrictStr): Organization ID of the Volume.
        state (StrictStr): State of the Volume.
        created_at (StrictStr): Date and time when the Volume was created.
        updated_at (StrictStr): Date and time when the Volume was last updated.
        last_used_at (StrictStr): Date and time when the Volume was last used.
    """

    @classmethod
    def from_dto(cls, dto: VolumeDto) -> "Volume":
        return cls(**dto.__dict__)


class VolumeService:
    """Service for managing Daytona Volumes. Can be used to list, get, create and delete Volumes."""

    def __init__(self, volumes_api: VolumesApi):
        self.__volumes_api = volumes_api

    def list(self) -> List[Volume]:
        """List all Volumes.

        Returns:
            List[Volume]: List of all Volumes.

        Example:
            ```python
            daytona = Daytona()
            volumes = daytona.volume.list()
            print(volumes)
            ```
        """
        return [Volume.from_dto(volume) for volume in self.__volumes_api.list_volumes()]

    def get(
        self, id: str
    ) -> Volume:  # TODO: volume - should be name # pylint: disable=fixme
        """Get a Volume by ID.

        Args:
            id (str): ID of the Volume to get.

        Returns:
            Volume: The Volume object.

        Example:
            ```python
            daytona = Daytona()
            volume = daytona.volume.get("test-volume-uuid")
            print(volume)
            ```
        """
        return Volume.from_dto(self.__volumes_api.get_volume(id))

    def create(self, name: str) -> Volume:
        """Create a new Volume.

        Args:
            name (str): Name of the Volume to create.

        Returns:
            Volume: The Volume object.

        Example:
            ```python
            daytona = Daytona()
            volume = daytona.volume.create("test-volume")
            print(volume)
            ```
        """
        return Volume.from_dto(
            self.__volumes_api.create_volume(CreateVolume(name=name))
        )

    def delete(
        self, id: str
    ) -> None:  # TODO: volume - should be name # pylint: disable=fixme
        """Delete a Volume by ID.

        Args:
            id (str): ID of the Volume to delete.

        Example:
            ```python
            daytona = Daytona()
            daytona.volume.delete("test-volume-uuid")
            ```
        """
        self.__volumes_api.delete_volume(id)


class SandboxVolumeService:
    """Service for managing Daytona Volumes in a Sandbox. Can be used to mount and unmount Volumes from a Sandbox."""

    def __init__(self, instance: SandboxInstance, toolbox_api: ToolboxApi):
        self.__instance = instance
        self.__toolbox_api = toolbox_api

    def mount(
        self, volume_id: str, path: str
    ) -> None:  # TODO: volume - should be volume name # pylint: disable=fixme
        """Mount a Volume to a Sandbox.

        Args:
            volume_id (str): ID of the Volume to mount.
            path (str): Path to mount the Volume to.

        Example:
            ```python
            daytona = Daytona()
            sandbox = daytona.create()
            sandbox.volume.mount("test-volume-uuid", "/mnt/test")
            ```
        """
        self.__toolbox_api.mount_volume(
            self.__instance.id, VolumeMountDto(volume_id=volume_id, path=path)
        )

    def unmount(
        self, volume_id: str
    ) -> None:  # TODO: volume - should be volume name # pylint: disable=fixme
        """Unmount a Volume from a Sandbox.

        Args:
            volume_id (str): ID of the Volume to unmount.

        Example:
            ```python
            daytona = Daytona()
            sandbox = daytona.create()
            sandbox.volume.mount("test-volume-uuid", "/mnt/test")
            # do some work
            sandbox.volume.unmount("test-volume-uuid")
            ```
        """
        self.__toolbox_api.unmount_volume(
            self.__instance.id, VolumeMountDto(volume_id=volume_id, path="/")
        )
