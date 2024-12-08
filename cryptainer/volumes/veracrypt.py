import os
import subprocess
from pathlib import Path
from cryptainer.logger import log
from cryptainer.volumes.base import VolumeTool

class VeraCryptTool(VolumeTool):
    """
    Tool class to manage VeraCrypt volumes.
    This class provides methods to create, mount, and unmount VeraCrypt volumes.
    """

    def create_volume(self, name: str, password: str, size: str = "1024M") -> str:
        """
        Create a new VeraCrypt volume.
        
        Args:
            name (str): Name of the volume.
            password (str): Password for securing the volume.
            size (str): Size of the volume (e.g., '10M' for 10 megabytes).

        Returns:
            str: The password used for the volume (for confirmation/logging purposes).

        Raises:
            FileExistsError: If a volume with the same name already exists.
            RuntimeError: If the VeraCrypt process fails.
        """
        volume_path = self.volume_dir / f"{name}"

        # Check if the volume already exists
        if volume_path.exists():
            raise FileExistsError(f"Container '{name}' already exists.")

        # Run the VeraCrypt command to create a new volume
        process = subprocess.run(
            [
                "veracrypt", "--text", "--create", str(volume_path),
                "--size", size, "--password", password,
                "--volume-type", "normal", "--encryption", "AES",
                "--hash", "sha-512", "--filesystem", "exfat", "--pim", "0",
                "--keyfiles", "", "--random-source", "/dev/urandom"
            ],
            check=True
        )
        
        # Check if the creation process succeeded
        if process.returncode != 0:
            raise RuntimeError("Failed to create VeraCrypt container")
        
        return password

    def mount_volume(self, name: str, password: str):
        """
        Mount an existing VeraCrypt volume.

        Args:
            name (str): Name of the volume to mount.
            password (str): Password to unlock the volume.

        Raises:
            Exception: If the VeraCrypt process fails, including error output.
        """
        volume_path = self.volume_dir / f"{name}"  # Path to the volume file
        mount_path = self.mount_dir / name  # Directory where the volume will be mounted

        # Ensure the mount directory exists
        os.makedirs(mount_path, exist_ok=True)

        # Run the VeraCrypt command to mount the volume, capturing stdout and stderr
        process = subprocess.run(
            [
                "veracrypt", "--text", "--mount", str(volume_path), str(mount_path),
                "--password", password, "--pim", "0", "--keyfiles", "", "--protect-hidden", "no"
            ],
            check=True
        )

        if process.returncode != 0:
            raise RuntimeError("Failed to mount VeraCrypt container")

    def unmount_volume(self, name: str):
        """
        Unmount a mounted VeraCrypt volume.

        Args:
            name (str): Name of the volume to unmount.

        Raises:
            Exception: If the VeraCrypt process fails, including error output.
        """
        mount_path = self.mount_dir / name  # Path to the mount directory
        volume_path = self.volume_dir / f"{name}"  # Path to the volume file

        # Run the VeraCrypt command to unmount the volume, capturing stdout and stderr
        process = subprocess.run(
            ["veracrypt", "--text", "--dismount", str(volume_path)],
            check=True
        )
        # Check if the creation process succeeded
        if process.returncode != 0:
            raise RuntimeError("Failed to dismount VeraCrypt container")
        
        # Remove the mount directory after unmounting
        try:
            os.rmdir(mount_path)  # Attempt to remove the empty mount directory
        except OSError as e:
            raise Exception(f"Error removing mount directory '{mount_path}': {e}")


if __name__ == "__main__":
    """
    Test the functionality of the VeraCryptTool class.
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

    # Initialize the VeraCrypt tool with test directories
    veracrypt_tool = VeraCryptTool(volume_dir, mount_dir)

    try:
        # Test creating, mounting, and unmounting a volume
        password = "securepassword123"
        size = "10M"

        # print("Creating volume...")
        # veracrypt_tool.create_volume("test_volume_001", password, size)
        # veracrypt_tool.create_volume("test_volume_002", password, size)

        # print("Mounting volume...")
        # veracrypt_tool.mount_volume("test_volume_001", password)
        # veracrypt_tool.mount_volume("test_volume_002", password)
        
        # print("Unmounting volume...")
        # veracrypt_tool.unmount_volume("test_volume_001")
        # veracrypt_tool.unmount_volume("test_volume_002")

    except Exception as e:
        log.error(e)