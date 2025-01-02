from cryptainer.volumes.gocryptfs import GocryptfsTool
from cryptainer.log import *
from cryptainer.password import generate_password
from cryptainer.config import DEFAULT_CONFIG_DIR
from pathlib import Path
from tabulate import tabulate
import subprocess, os

class VolumeController:
    """
    A controller class to manage encrypted volumes using various tools (e.g., gocryptfs).
    """

    VOLUMES_META_FILE = DEFAULT_CONFIG_DIR / 'volumes.json'

    def __init__(self, volume_dir: str, mount_dir: str):
        """
        Initialize the VolumeController.
        
        Args:
            volume_dir (str): Directory where volumes are stored.
            mount_dir (str): Directory where volumes are mounted.
        """
        self.volume_dir = Path(volume_dir).expanduser()
        self.mount_dir = Path(mount_dir).expanduser()
        self._mount_cmd_result = None

        # Initialize volume tools
        self.tools = {
            "gocryptfs": GocryptfsTool(),
        }

    def list_volumes(self, show_unknown_fs: bool = False):
        """
        List all volumes in the volume directory, showing their status (mounted/unmounted).
        """
        volumes_headers = ["Volume name", "Type", "Mounted?", "Mount path"]
        volumes_data = []

        # Store the mount command result
        self._mount_cmd_result = self._run_mount_cmd()

        print_info(f"Available volumes ({self.volume_dir})")

        # Iterate over all items in the volume directory, sorted by creation date
        for item in sorted(self.volume_dir.iterdir(), key=lambda x: x.stat().st_ctime):
            is_mounted, mount_path = self.is_mounted(item.name)
            volume_type = self.detect_volume_type(item.name)

            if volume_type != 'unknown' or show_unknown_fs:
                volumes_data.append([
                    item.name, volume_type, is_mounted, mount_path
                ])

        # Display the results in a tabular format
        print()
        print(tabulate(volumes_data, headers=volumes_headers, tablefmt=""))

    def create_volume(self, volume_type: str, name: str, password: str = None, size: str = None):
        """
        Create a new encrypted volume.

        Args:
            volume_type (str): The type of volume to create (e.g., 'gocryptfs').
            name (str): The name of the new volume.
            password (str, optional): The password for the volume. If None, a random password is generated.
            size (str, optional): Size of the volume (if applicable to the tool).
        """
        print_info(f"Creating {volume_type} volume: {name}")

        try:
            tool = self.tools[volume_type]
            volume_password = generate_password(30, use_special=False)  # Generate a random password
            volume_path = self.volume_dir / name
            
            tool.create_volume(volume_path, volume_password, size)

            print_success(f"Volume successfully created with password: {volume_password}")
        except Exception as e:
            print_error(e)

    def mount_volume(self, name: str):
        """
        Mount an existing volume.

        Args:
            name (str): The name of the volume to mount.
        """
        print_info(f"Mounting volume: {name}")

        volume_type = self.detect_volume_type(name)
        if volume_type == "unknown":
            print_error(f"Volume type for '{name}' is unknown. Cannot mount.")
            return

        try:
            volume_password = prompt(f"Enter password for {name}: ")
            tool = self.tools.get(volume_type)

            mount_path = self.mount_dir / name
            volume_path = self.volume_dir / name

            tool.mount_volume(volume_path, mount_path, volume_password)
            print_success(f"Volume {name} mounted at '{mount_path}'")
        except Exception as e:
            print_error(e)

    def unmount_volume(self, name: str):
        """
        Unmount a mounted volume.

        Args:
            name (str): The name of the volume to unmount.
        """
        print_info(f"Unmounting volume: {name}")

        volume_type = self.detect_volume_type(name)
        if volume_type == "unknown":
            print_error(f"Volume type for '{name}' is unknown. Cannot unmount.")
            return

        try:
            tool = self.tools.get(volume_type)
            mount_path = self.mount_dir / name

            tool.unmount_volume(mount_path)
            print_success(f"Volume '{name}' unmounted and mount directory removed.")
        except Exception as e:
            print_error(e)

    def is_mounted(self, name: str):
        """
        Check if a volume is mounted.

        Args:
            name (str): The name of the volume.

        Returns:
            (bool, str): A tuple where the first element indicates if the volume is mounted,
                         and the second element is the mount path (empty if not mounted).
        """
        mount_path = self.mount_dir / name
        if str(mount_path) in self._mount_cmd_result:
            return True, str(mount_path)
        return False, ""

    def detect_volume_type(self, name: str):
        """
        Detect the type of an encrypted volume based on its structure.

        Args:
            name (str): The name of the volume.

        Returns:
            str: The type of the volume (e.g., 'gocryptfs').
        """
        volume_path = self.volume_dir / name
        if volume_path.is_dir() and Path(volume_path / "gocryptfs.conf").exists():
            return "gocryptfs"
        else:
            print_debug(f"Unable to detect volume type for '{name}'", False)
        return "unknown"

    def get_mounted_volumes(self):
        """
        Get a list of names of all mounted volumes.

        Returns:
            list: Names of mounted volumes.
        """
        self._mount_cmd_result = self._run_mount_cmd()
        return [item.name for item in self.volume_dir.iterdir() if self.is_mounted(item.name)[0]]

    def get_unmounted_volumes(self):
        """
        Get a list of names of all unmounted volumes.

        Returns:
            list: Names of unmounted volumes.
        """
        self._mount_cmd_result = self._run_mount_cmd()
        return [item.name for item in self.volume_dir.iterdir() if not self.is_mounted(item.name)[0]]

    def _run_mount_cmd(self):
        """
        Run the `mount` command to get the list of currently mounted volumes.

        Returns:
            str: Output of the `mount` command.
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
            print_error(f"Error checking mount status: {e}")
            return ""
