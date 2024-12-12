import os
import subprocess
from pathlib import Path
from cryptainer.volumes.base import VolumeTool

class GocryptfsTool(VolumeTool):
    """
    Tool class to manage Gocryptfs volumes.
    This class provides methods to create, mount, and unmount encrypted Gocryptfs volumes.
    """

    def create_volume(self, name: str, password: str, size: str = None) -> str:
        """
        Create a new Gocryptfs volume.

        Args:
            name (str): Name of the volume.
            password (str): Password for securing the volume.
            size (str, optional): Size is not used directly by Gocryptfs, 
                                  but included for interface compatibility.

        Returns:
            str: The password used for the volume (for confirmation/logging purposes).

        Raises:
            FileExistsError: If a volume with the same name already exists.
        """
        volume_path = self.volume_dir / f"{name}"  # Path to the volume directory

        # Check if the volume already exists
        if volume_path.exists():
            raise FileExistsError(f"Volume '{name}' already exists.")

        # Ensure the volume directory exists
        os.makedirs(volume_path, exist_ok=True)
        
        # Initialize the Gocryptfs volume
        process = subprocess.run(
            ["gocryptfs", "-init", "-passfile", "/dev/stdin", str(volume_path)],
            input=password,  # Pass the password through stdin
            text=True,
            check=True  # Raise an error if the command fails
        )

        if process.returncode != 0:
            raise RuntimeError("Failed to create Gocryptfs container")
        
        return password

    def mount_volume(self, name: str, password: str):
        """
        Mount an existing Gocryptfs volume.

        Args:
            name (str): Name of the volume to mount.
            password (str): Password to unlock the volume.

        Raises:
            Exception: If the Gocryptfs process fails.
        """
        volume_path = self.volume_dir / f"{name}"  # Path to the encrypted volume
        mount_path = self.mount_dir /  f"{name}"  # Directory to mount the volume

        # Ensure the mount directory exists
        os.makedirs(mount_path, exist_ok=True)

        # Mount the Gocryptfs volume
        process = subprocess.run(
            ["gocryptfs", "-passfile", "/dev/stdin", str(volume_path), str(mount_path)],
            input=password,  # Pass the password through stdin
            text=True,
            check=True  # Raise an error if the command fails
        )

        if process.returncode != 0:
            raise RuntimeError("Failed to mount Gocryptfs container")

    def unmount_volume(self, name: str):
        """
        Unmount a mounted Gocryptfs volume.

        Args:
            name (str): Name of the volume to unmount.

        Raises:
            Exception: If the unmount process fails.
        """
        mount_path = self.mount_dir / f"{name}"  # Path to the mount directory

        # Unmount the Gocryptfs volume
        process = subprocess.run(["fusermount", "-u", str(mount_path)], check=True)

        if process.returncode != 0:
            raise RuntimeError("Failed to mount Gocryptfs container")

        # Remove the mount directory after unmounting
        try:
            os.rmdir(mount_path)  # Attempt to remove the empty mount directory
        except OSError as e:
            print(f"Error removing mount directory '{mount_path}': {e}")


if __name__ == "__main__":
    """
    Test the functionality of the GocryptfsTool class.
    Includes:
    - Volume creation
    - Volume mounting
    - Volume unmounting
    """

    # Directories for storing volumes and mounts (used for testing)
    volume_dir = Path("./tests/volumes")
    mount_dir = Path("./tests/mounts")
    
    # Create the directories if they do not exist
    volume_dir.mkdir(parents=True, exist_ok=True)
    mount_dir.mkdir(parents=True, exist_ok=True)

    # Initialize the Gocryptfs tool with test directories
    gocryptfs_tool = GocryptfsTool(volume_dir, mount_dir)

    try:
        # Test creating, mounting, and unmounting a volume
        password = "securepassword123"
        size = "10M"

        # print("Creating volume...")
        gocryptfs_tool.create_volume("test_volume_001", password)
        # gocryptfs_tool.create_volume("test_volume_002", password, size)

        # print("Mounting volume...")
        # gocryptfs_tool.mount_volume("test_volume_001", password)
        # gocryptfs_tool.mount_volume("test_volume_002", password)
        
        # print("Unmounting volume...")
        # gocryptfs_tool.unmount_volume("test_volume_001")
        # gocryptfs_tool.unmount_volume("test_volume_002")

    except Exception as e:
        print(e)