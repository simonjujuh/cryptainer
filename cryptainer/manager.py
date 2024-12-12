from cryptainer.volumes.veracrypt import VeraCryptTool
from cryptainer.volumes.gocryptfs import GocryptfsTool
from cryptainer.logger import log
from cryptainer.config import DEFAULT_CONFIG_DIR
from pathlib import Path
import subprocess
import json


class VolumeManager:
    """
    A manager class for handling encrypted volumes.
    Stores metadata in a centralized 'meta.json' file.
    """

    VOLUMES_META_FILE = DEFAULT_CONFIG_DIR / 'volumes.json'

    def __init__(self, volume_dir: str, mount_dir: str):
        """
        Initialize the VolumeManager with directories for volumes and mounts.

        Args:
            volume_dir (str): Path to the directory where volumes are stored.
            mount_dir (str): Path to the directory where volumes will be mounted.
        """
        self.volume_dir = Path(volume_dir).expanduser()
        self.mount_dir = Path(mount_dir).expanduser()

        # Initialize volume tools
        self.tools = {
            "gocryptfs": GocryptfsTool(self.volume_dir, self.mount_dir),
            "veracrypt": VeraCryptTool(self.volume_dir, self.mount_dir),
        }

        # Bette store the command output in a variable rather than running it multiple times
        self._mount_cmd_result = self._run_mount_cmd()

        # Ensure metadata file exists
        self.meta_file = self.VOLUMES_META_FILE
        self.metadata = self._load_metadata()


    def _run_mount_cmd(self):
        """
        """
        try:
            result = subprocess.run(
                ["mount"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return result
        except Exception as e:
            log.error(f"Error checking mount status")

    def _load_metadata(self):
        """
        Load metadata from the meta.json file.
        """
        if self.meta_file.exists():
            with open(self.meta_file, "r") as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        """
        Save metadata to the meta.json file.
        """
        with open(self.meta_file, "w") as f:
            json.dump(self.metadata, f, indent=4)

    def register_volume(self, name: str, volume_type: str, path):
        """
        Register a new volume in the metadata.

        Args:
            name (str): Name of the volume.
            volume_type (str): Type of the volume (e.g., "veracrypt", "gocryptfs").
            path (str): Path to the volume file.
        """
        self.metadata[name] = {
            "type": volume_type,
            "path": path.resolve(),
        }
        self._save_metadata()

    def get_volume_info(self, name: str):
        """
        Get metadata information for a specific volume.

        Args:
            name (str): Name of the volume.

        Returns:
            dict: Metadata for the volume, or None if not found.
        """
        return self.metadata.get(name)

    def list_volumes(self):
        """
        List all volumes present in the volume directory, along with their type and mount status.
        """
        log.info("Available volumes:")
        for item in self.volume_dir.iterdir():
            # Retrieve volume info from metadata
            volume_info = self.metadata.get(item.name)
            if not volume_info:
                volume_type = "unknown"
                log.warning(f"Can not get info for volume {volume_info}")
            else:
                volume_type = volume_info.get("type", "unknown")
                is_mounted, path = self.is_mounted(item.name)
                path = Path(path)

            if is_mounted:
                log.success(f"{item.name:30} [{volume_type}, mounted:{path.resolve()}]")
            else:
                log.info(f"{item.name:30} [{volume_type}")



    def is_mounted(self, name: str):
        """
        Check if a volume is mounted and return its mount path if it is.

        Args:
            name (str): Name of the volume to check.

        Returns:
            (bool, str): Tuple containing a boolean indicating mount status and the mount path (or empty string if not mounted).
        """
        mount_path = self.mount_dir / name

        # Vérification dans la sortie de la commande mount
        if str(mount_path) in self._mount_cmd_result.stdout:
            return True, str(mount_path)

        return False, ""

    def get_mounted_volume_names(self):
        """
        """
        pass
        # return [volume['name'] for volume in self.volumes if volume.get('mount_path') is not None]

    def get_unmounted_volume_names(self):
        """
        """
        pass
        # return [volume['name'] for volume in self.volumes if volume.get('mount_path') is None]

    def create_volume(self, volume_type: str, name: str, password: str, size: str = None, auto_mount: bool = False):
        """
        Create a new volume and add its metadata to 'meta.json'.

        Args:
            volume_type (str): Type of the volume ('gocryptfs' or 'veracrypt').
            name (str): Name of the new volume.
            password (str): Password for securing the volume.
            size (str, optional): Size of the volume (required for VeraCrypt).
            auto_mount (bool): Automatically mount the volume after creation.

        Raises:
            Exception: If the volume creation fails.
        """
        pass
        # if volume_type not in self.tools:
        #     raise(f"Unsupported volume type: {volume_type}")

        # # volumes with same name but different extensions are not allowed
        # for extension in self.extensions.values():
        #     volume_path = self.volume_dir / f"{name}{extension}"
            
        #     if volume_path.exists() and extension == self.extensions[volume_type]:
        #         raise FileExistsError(f"{volume_path} already exists")
        #     elif volume_path.exists():
        #         raise FileExistsError(f"{volume_path} with extension {extension} already exists")
        
        # # Create the volume
        # tool = self.tools[volume_type]
        # try:
        #     tool.create_volume(name, password, size)

        #     log.info(f"{volume_type.capitalize()} volume '{name}' created successfully with password: {password}")
        #     if auto_mount:
        #         tool.mount_volume(name, password)
        #         log.info(f"Volume '{name}' mounted successfully.")
        # except Exception as e:
        #     log.error(f"Error creating volume '{name}': {e}")

    def mount_volume(self, name: str, password: str):
        """
        Mount a specific volume.

        Args:
            name (str): Name of the volume.
            password (str): Password to unlock the volume.

        Raises:
            Exception: If the volume mounting fails.
        """
        # récupère le nom du volume
        # identifie le type de conteneur
        # configure le tool associé au type de conteneur
        # appel la methode unmount du tool
        pass
        # if volume_type == "unknown":
        #     log.error(f"Volume type for '{name}' is unknown. Cannot mount.")
        #     return

        # tool = self.tools[volume_type]
        # try:
        #     tool.mount_volume(name, password)
        #     log.info(f"Volume '{name}' mounted successfully.")
        # except Exception as e:
        #     log.error(f"Error mounting volume '{name}': {e}")

    def unmount_volume(self, name: str):
        """
        Unmount a specific volume and remove the mount directory.

        Args:
            name (str): Name of the volume.

        Raises:
            Exception: If the unmounting process fails.
        """
        # récupère le nom du volume
        # identifie le type de conteneur
        # configure le tool associé au type de conteneur
        # appel la methode unmount du tool
        pass
        # volume_type = self.detect_volume_type(name)
        # if volume_type == "unknown":
        #     log.error(f"Volume type for '{name}' is unknown. Cannot unmount.")
        #     return

        # tool = self.tools[volume_type]
        # try:
        #     tool.unmount_volume(name)
        #     mount_path = self.mount_dir / name
        #     if mount_path.exists():
        #         os.rmdir(mount_path)  # Remove the empty mount directory
        #     log.info(f"Volume '{name}' unmounted and mount directory removed.")
        # except Exception as e:
        #     log.error(f"Error unmounting volume '{name}': {e}")


# Example usage
if __name__ == "__main__":
    """
    Example for testing the VolumeManager functionality.
    """
    volume_manager = VolumeManager(volume_dir="./tests/volumes", mount_dir="./tests/mounts")

    # print(volume_manager.get_mounted_volume_names())
    # print(volume_manager.get_unmounted_volume_names())

    # Create a new VeraCrypt volume
    # volume_manager.create_volume("veracrypt", "test_01", "password123", "100M")
    # volume_manager.create_volume("veracrypt", "test_02", "password1234", "100M")
    # volume_manager.create_volume("gocryptfs", "test_03", "password123")

    # # Mount a volume
    # volume_manager.mount_volume("gocryptfs_test_01", "password123")

    # List volumes
    volume_manager.list_volumes()

    # Unmount a volume
    # volume_manager.unmount_volume("gocryptfs_test_01")
    # volume_manager.list_volumes()
