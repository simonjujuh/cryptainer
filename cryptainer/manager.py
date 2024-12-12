from cryptainer.volumes.veracrypt import VeraCryptTool
from cryptainer.volumes.gocryptfs import GocryptfsTool
from cryptainer.logger import log
from cryptainer.config import DEFAULT_CONFIG_DIR
from pathlib import Path
import subprocess
import json, os


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
            return result.stdout
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

    def list_volumes(self):
        """
        List all volumes present in the volume directory, including their type and mount status.
        This method iterates over the volume directory and retrieves information about each volume 
        from the metadata file. It logs the volume name, type, and mount status (if mounted or not).
        """
        log.info("Available volumes:")
        
        # Iterate over all items in the volume directory
        # by stat creation date : sorted(self.volume_dir.iterdir(), key=lambda x: x.stat().st_ctime)
        # by name : sorted(self.volume_dir.iterdir(), key=lambda x: x.name.lower())
        for item in sorted(self.volume_dir.iterdir(), key=lambda x: x.stat().st_ctime):
            # Retrieve volume information from the metadata
            volume_info = self.metadata.get(item.name)

            # Check if volume information is available, else log a warning
            if volume_info is None:
                volume_type = "unknown"
                log.warning(f"Cannot retrieve info for volume: {item.name}")
            else:
                volume_type = volume_info.get("type", "unknown")

            # Check if the volume is mounted and get the mount path
            is_mounted, mount_path = self.is_mounted(item.name)
            mount_path = Path(mount_path)  # Ensure the mount path is a Path object

            # Format and log the volume status
            if is_mounted:
                # If mounted, display the full path
                log.success(f"{item.name:30} [{volume_type}] :: {mount_path.resolve()} ")
            else:
                # If not mounted, display "not mounted"
                log.info(f"{item.name:30} [{volume_type}]")

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
        if str(mount_path) in self._mount_cmd_result:
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
        # Check if the provided volume type is supported
        if volume_type not in self.tools:
            raise ValueError(f"Unsupported volume type: {volume_type}")

        # Check if the volume with the same name already exists in the volume directory
        volume_path = self.volume_dir / name
        if volume_path.exists():
            raise FileExistsError(f"A volume with the name '{name}' already exists in the volume directory.")

        # Select the tool based on the volume type
        tool = self.tools[volume_type]

        try:
            # Create the volume using the appropriate tool
            log.info(f"Creating {volume_type.capitalize()} volume '{name}'...")

            # If the volume is VeraCrypt, we need to pass the size argument
            if volume_type == "veracrypt" and size is None:
                raise ValueError("Size is required for VeraCrypt volumes.")
            
            # Create the volume
            tool.create_volume(name, password, size)

            # After creation, log success
            log.success(f"{volume_type.capitalize()} volume '{name}' created successfully with password: {password}")

            # Add metadata for the created volume (optional: for your 'meta.json' or similar storage)
            self.metadata[name] = {"type": volume_type, "path": str(volume_path.resolve())}
            self._save_metadata()

            # If auto_mount is enabled, attempt to mount the volume
            if auto_mount:
                log.info(f"Attempting to mount '{name}' after creation...")
                tool.mount_volume(name, password)
                log.info(f"Volume '{name}' mounted successfully.")

        except Exception as e:
            # Log any errors during volume creation or mounting
            log.error(f"Error creating volume '{name}': {str(e)}")
            raise e
        
        self._mount_cmd_result = self._run_mount_cmd()

    def mount_volume(self, name: str, password: str):
        """
        Mount a specific volume.

        Args:
            name (str): Name of the volume.
            password (str): Password to unlock the volume.

        Raises:
            Exception: If the volume mounting fails.
        """
        # Step 1: Retrieve volume metadata
        volume_info = self.metadata.get(name)
        if not volume_info:
            log.error(f"Volume '{name}' not found in metadata. Cannot mount.")
            return

        volume_type = volume_info.get("type", "unknown")
        if volume_type == "unknown":
            log.error(f"Volume type for '{name}' is unknown. Cannot mount.")
            return

        # Step 2: Configure the tool based on the volume type
        tool = self.tools.get(volume_type)
        if not tool:
            log.error(f"No tool available for volume type '{volume_type}'. Cannot mount.")
            return

        # Step 3: Call the mount method of the tool
        try:
            mount_path = self.mount_dir / name  # Mount point
            mount_path.mkdir(parents=True, exist_ok=True)  # Ensure mount point exists

            tool.mount_volume(name=name, password=password)
            log.info(f"Volume '{name}' of type '{volume_type}' mounted successfully at '{mount_path}'.")
        except Exception as e:
            log.error(f"Error mounting volume '{name}': {e}")
        
        self._mount_cmd_result = self._run_mount_cmd()

    def unmount_volume(self, name: str):
        """
        Unmount a specific volume and remove the mount directory.

        Args:
            name (str): Name of the volume.

        Raises:
            Exception: If the unmounting process fails.
        """
        # Step 1: Retrieve volume metadata
        volume_info = self.metadata.get(name)
        if not volume_info:
            log.error(f"Volume '{name}' not found in metadata. Cannot unmount.")
            return

        volume_type = volume_info.get("type", "unknown")
        if volume_type == "unknown":
            log.error(f"Volume type for '{name}' is unknown. Cannot unmount.")
            return

        # Step 2: Configure the tool based on the volume type
        tool = self.tools.get(volume_type)
        if not tool:
            log.error(f"No tool available for volume type '{volume_type}'. Cannot unmount.")
            return

        # Step 3: Call the unmount method of the tool
        try:
            mount_path = self.mount_dir / name  # Mount point

            tool.unmount_volume(name=name)
            if mount_path.exists() and mount_path.is_dir():
                os.rmdir(mount_path)  # Remove the empty mount directory
            log.info(f"Volume '{name}' of type '{volume_type}' unmounted and mount directory removed.")
        except Exception as e:
            log.error(f"Error unmounting volume '{name}': {e}")
        
        self._mount_cmd_result = self._run_mount_cmd()

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

    # # List volumes
    # volume_manager.list_volumes()

    # # Mount a volume
    # volume_manager.mount_volume("test_03", "password123")

    # # List volumes
    # volume_manager.list_volumes()

    # # Unmount a volume
    # volume_manager.unmount_volume("test_03")

    # # List volumes
    # volume_manager.list_volumes()

    # volume_manager.list_volumes()
