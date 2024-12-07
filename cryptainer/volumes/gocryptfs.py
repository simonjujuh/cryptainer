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
        subprocess.run(
            ["gocryptfs", "-init", "-passfile", "/dev/stdin", str(volume_path)],
            input=password,  # Pass the password through stdin
            text=True,
            check=True  # Raise an error if the command fails
        )
        
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
        mount_path = self.mount_dir / name  # Directory to mount the volume

        # Ensure the mount directory exists
        os.makedirs(mount_path, exist_ok=True)

        # Mount the Gocryptfs volume
        subprocess.run(
            ["gocryptfs", "-passfile", "/dev/stdin", str(volume_path), str(mount_path)],
            input=password,  # Pass the password through stdin
            text=True,
            check=True  # Raise an error if the command fails
        )

    def unmount_volume(self, name: str):
        """
        Unmount a mounted Gocryptfs volume.

        Args:
            name (str): Name of the volume to unmount.

        Raises:
            Exception: If the unmount process fails.
        """
        mount_path = self.mount_dir / name  # Path to the mount directory

        # Unmount the Gocryptfs volume
        subprocess.run(["fusermount", "-u", str(mount_path)], check=True)

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
    - Cleanup after testing
    """

    # Directories for storing volumes and mounts (used for testing)
    volume_dir = Path("./tests/volumes")
    mount_dir = Path("./tests/mounts")
    
    # Create the directories if they do not exist
    volume_dir.mkdir(parents=True, exist_ok=True)
    mount_dir.mkdir(parents=True, exist_ok=True)

    # Initialize the Gocryptfs tool with test directories
    gocryptfs_tool = GocryptfsTool(volume_dir, mount_dir)

    # Test parameters
    volume_name = "test_volume"  # Name of the test volume
    password = "securepassword123"  # Test password for the volume

    try:
        # Test: Create a new volume
        print("\n--- Test: Creating a new volume ---")
        gocryptfs_tool.create_volume(volume_name, password)
        print(f"Volume '{volume_name}' created successfully.")
    except FileExistsError:
        print(f"Error: Volume '{volume_name}' already exists.")
    except Exception as e:
        print(f"Error during volume creation: {e}")

    try:
        # Test: Mount the created volume
        print("\n--- Test: Mounting the volume ---")
        gocryptfs_tool.mount_volume(volume_name, password)
        print(f"Volume '{volume_name}' mounted successfully.")
    except Exception as e:
        print(f"Error during volume mounting: {e}")

    try:
        # Test: Unmount the mounted volume
        print("\n--- Test: Unmounting the volume ---")
        gocryptfs_tool.unmount_volume(volume_name)
        print(f"Volume '{volume_name}' unmounted successfully.")
    except Exception as e:
        print(f"Error during volume unmounting: {e}")

    # Cleanup: Delete the test volume after unmounting
    # print("\n--- Cleanup ---")
    # try:
    #     test_volume_path = volume_dir / volume_name
    #     print(test_volume_path)
    #     if test_volume_path.exists():
    #         os.rmdir(test_volume_path)  # Remove the test volume directory
    #         print(f"Volume '{volume_name}' deleted successfully.")
    # except Exception as e:
    #     print(f"Error during volume deletion: {e}")
