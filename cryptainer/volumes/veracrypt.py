import os
import subprocess
from pathlib import Path
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
            RuntimeError: If the VeraCrypt creation process fails.
        """
        volume_path = self.volume_dir / f"{name}"  # Path to the volume file

        # Check if the volume already exists
        if volume_path.exists():
            raise FileExistsError(f"Container '{name}' already exists.")

        # Ensure the volume directory exists
        os.makedirs(self.volume_dir, exist_ok=True)

        try:
            # Run the VeraCrypt command to create a new volume
            subprocess.run(
                [
                    "veracrypt", "--text", "--create", str(volume_path),
                    "--size", size, "--password", password,
                    "--volume-type", "normal", "--encryption", "AES",
                    "--hash", "sha-512", "--filesystem", "exfat", "--pim", "0",
                    "--keyfiles", "", "--random-source", "/dev/urandom"
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to create VeraCrypt container '{name}': {str(e)}")

        return password

    def mount_volume(self, name: str, password: str):
        """
        Mount an existing VeraCrypt volume.

        Args:
            name (str): Name of the volume to mount.
            password (str): Password to unlock the volume.

        Raises:
            FileNotFoundError: If the volume doesn't exist.
            RuntimeError: If the VeraCrypt mounting process fails.
        """
        volume_path = self.volume_dir / f"{name}"  # Path to the volume file
        mount_path = self.mount_dir / f"{name}"  # Directory where the volume will be mounted

        # Ensure the volume exists
        if not volume_path.exists():
            raise FileNotFoundError(f"Volume '{name}' does not exist at {volume_path}.")

        # Ensure the mount directory exists
        os.makedirs(mount_path, exist_ok=True)

        try:
            # Run the VeraCrypt command to mount the volume
            subprocess.run(
                [
                    "veracrypt", "--text", "--mount", str(volume_path), str(mount_path),
                    "--password", password, "--pim", "0", "--keyfiles", "", "--protect-hidden", "no"
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to mount VeraCrypt container '{name}': {str(e)}")

    def unmount_volume(self, name: str):
        """
        Unmount a mounted VeraCrypt volume.

        Args:
            name (str): Name of the volume to unmount.

        Raises:
            FileNotFoundError: If the volume doesn't exist.
            RuntimeError: If the VeraCrypt unmounting process fails.
        """
        volume_path = self.volume_dir / f"{name}"  # Path to the volume file
        mount_path = self.mount_dir / f"{name}"  # Directory where the volume is mounted

        # Ensure the volume exists
        if not volume_path.exists():
            raise FileNotFoundError(f"Volume '{name}' does not exist at {volume_path}.")

        try:
            # Run the VeraCrypt command to unmount the volume
            subprocess.run(
                ["veracrypt", "--text", "--dismount", str(volume_path)],
                check=True,
            )

            # Remove the mount directory after unmounting
            os.rmdir(mount_path)  # Attempt to remove the empty mount directory
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to unmount VeraCrypt container '{name}': {str(e)}")
        except OSError as e:
            raise RuntimeError(f"Error removing mount directory '{mount_path}': {e}")



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

        # Test 1: Simple volume creation
        # veracrypt_tool.create_volume("test_volume_001", password)

        # # Test 2: Creating an already existing volume
        # veracrypt_tool.create_volume("test_volume_001", password)

        # Test 3: Simple volume mounting
        # veracrypt_tool.mount_volume("test_volume_002", password)

        # Test 4: Mounting a non-existing volume
        # veracrypt_tool.mount_volume("non_existing_volume", password)
        
        # Test 5: Mounting a volume that's already mounted
        # veracrypt_tool.mount_volume("test_volume_002", password)
        
        # Test 6: Simple volume unmounting
        # veracrypt_tool.unmount_volume("test_volume_002")

        # Test 7: Unmounting a non-existing mount point
        # veracrypt_tool.unmount_volume("non_existing_volume")

        # Test 8: Unmounting an already unmounted volume
        # veracrypt_tool.unmount_volume("test_volume_001")

    except Exception as e:
        print(e)
        pass # with veracrypt, stdout and stderr are printed out, because it might expect password 