import os
import subprocess
from pathlib import Path
from cryptainer.volumes.base import VolumeTool

class VeraCryptTool(VolumeTool):
    """
    Tool class to manage VeraCrypt volumes.
    This class provides methods to create, mount, and unmount VeraCrypt volumes.
    """

    def create_volume(self, name: str, size: str, password: str) -> str:
        """
        Create a new VeraCrypt volume.
        
        Args:
            name (str): Name of the volume.
            size (str): Size of the volume (e.g., '10M' for 10 megabytes).
            password (str): Password for securing the volume.

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
            raise RuntimeError("Failed to create VeraCrypt container.")
        
        return password

    def mount_volume(self, name: str, password: str):
        """
        Mount an existing VeraCrypt volume.
        
        Args:
            name (str): Name of the volume to mount.
            password (str): Password to unlock the volume.

        Raises:
            Exception: If the VeraCrypt process fails.
        """
        volume_path = self.volume_dir / f"{name}"  # Path to the volume file
        mount_path = self.mount_dir / name  # Directory where the volume will be mounted

        # Ensure the mount directory exists
        os.makedirs(mount_path, exist_ok=True)

        # Run the VeraCrypt command to mount the volume
        subprocess.run(
            [
                "veracrypt", "--text", "--mount", str(volume_path), str(mount_path),
                "--password", password, "--pim", "0", "--keyfiles", "", "--protect-hidden", "no"
            ],
            check=True
        )

    def unmount_volume(self, name: str):
        """
        Unmount a mounted VeraCrypt volume.
        
        Args:
            name (str): Name of the volume to unmount.

        Raises:
            Exception: If the VeraCrypt process fails.
        """
        mount_path = self.mount_dir / name  # Path to the mount directory
        volume_path = self.volume_dir / f"{name}"  # Path to the volume file

        # Run the VeraCrypt command to unmount the volume
        subprocess.run(["veracrypt", "--text", "--dismount", str(volume_path)], check=True)

        # Remove the mount directory after unmounting
        try:
            os.rmdir(mount_path)  # Attempt to remove the empty mount directory
        except OSError as e:
            print(f"Error removing mount directory '{mount_path}': {e}")

if __name__ == "__main__":
    """
    Test the functionality of the VeraCryptTool class.
    Includes:
    - Volume creation
    - Volume mounting
    - Volume unmounting
    - Cleanup after testing
    """

    # Directories for storing volumes and mounts (used for testing)
    volume_dir = Path("./tests/volumes")
    mount_dir = Path("./tests/mounts")
    
    # Create the directories if they do not exist
    volume_dir.mkdir(parents=True, exist_ok=True)
    mount_dir.mkdir(parents=True, exist_ok=True)

    # Initialize the VeraCrypt tool with test directories
    veracrypt_tool = VeraCryptTool(volume_dir, mount_dir)

    # Test parameters
    volume_name = "test_volume"  # Name of the test volume
    volume_size = "10M"          # Small size for test purposes
    password = "securepassword123"  # Test password for the volume

    try:
        # Test: Create a new volume
        print("\n--- Test: Creating a new volume ---")
        veracrypt_tool.create_volume(volume_name, volume_size, password)
        print(f"Volume '{volume_name}' created successfully.")
    except FileExistsError:
        print(f"Error: Volume '{volume_name}' already exists.")
    except Exception as e:
        print(f"Error during volume creation: {e}")

    try:
        # Test: Mount the created volume
        print("\n--- Test: Mounting the volume ---")
        veracrypt_tool.mount_volume(volume_name, password)
        print(f"Volume '{volume_name}' mounted successfully.")
    except Exception as e:
        print(f"Error during volume mounting: {e}")

    try:
        # Test: Unmount the mounted volume
        print("\n--- Test: Unmounting the volume ---")
        veracrypt_tool.unmount_volume(volume_name)
        print(f"Volume '{volume_name}' unmounted successfully.")
    except Exception as e:
        print(f"Error during volume unmounting: {e}")

    # Cleanup: Delete the test volume after unmounting
    # print("\n--- Cleanup ---")
    # try:
    #     test_volume_path = volume_dir / volume_name
    #     print(test_volume_path.exists())
    #     if test_volume_path.exists():
    #         test_volume_path.unlink()  # Remove the test volume file
    #         print(f"Volume '{volume_name}' deleted successfully.")
    # except Exception as e:
    #     print(f"Error during volume deletion: {e}")
