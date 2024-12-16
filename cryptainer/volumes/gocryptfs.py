import os
import subprocess
from pathlib import Path
from cryptainer.volumes.base import VolumeTool


class GocryptfsTool(VolumeTool):
    """
    Tool class to manage Gocryptfs volumes.
    Provides methods to create, mount, and unmount encrypted Gocryptfs volumes.
    """

    def create_volume(self, name: str, password: str, size: str = None) -> str:
        """
        Create a new Gocryptfs volume.

        Args:
            name (str): Name of the volume.
            password (str): Password for securing the volume.
            size (str, optional): Included for interface compatibility.

        Returns:
            str: The password used for the volume (for confirmation/logging purposes).

        Raises:
            FileExistsError: If a volume with the same name already exists.
            RuntimeError: If the Gocryptfs initialization fails.
        """
        volume_path = self.volume_dir / f"{name}"  # Path to the volume directory

        # Check if the volume already exists
        if volume_path.exists():
            raise FileExistsError(f"Volume '{name}' already exists.")

        # Ensure the volume directory exists
        os.makedirs(volume_path, exist_ok=True)

        try:
            # Initialize the Gocryptfs volume
            subprocess.run(
                ["gocryptfs", "-q", "-init", "-passfile", "/dev/stdin", str(volume_path)],
                input=password,  # Pass the password through stdin
                text=True,
                check=True,  # Automatically raise CalledProcessError on failure
                stderr=subprocess.PIPE,  # Capture stderr pour éviter qu'il ne s'affiche
                stdout=subprocess.PIPE,  # Capture stdout si nécessaire
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to create Gocryptfs volume '{name}': {e.stderr or e}")

        return password

    def mount_volume(self, name: str, password: str):
        """
        Mount an existing Gocryptfs volume.

        Args:
            name (str): Name of the volume to mount.
            password (str): Password to unlock the volume.

        Raises:
            FileNotFoundError: If the volume doesn't exist.
            RuntimeError: If the mounting process fails.
        """
        volume_path = self.volume_dir / f"{name}"  # Path to the encrypted volume
        mount_path = self.mount_dir / f"{name}"  # Directory to mount the volume

        # Ensure the volume exists
        if not volume_path.exists():
            raise FileNotFoundError(f"Volume '{name}' does not exist")

        # Ensure the mount directory exists
        os.makedirs(mount_path, exist_ok=True)

        try:
            # Mount the Gocryptfs volume
            subprocess.run(
                ["gocryptfs", "-q", "-passfile", "/dev/stdin", str(volume_path), str(mount_path)],
                input=password,  # Pass the password through stdin
                text=True,
                check=True,  # Automatically raise CalledProcessError on failure
                stderr=subprocess.PIPE,  # Capture stderr pour éviter qu'il ne s'affiche
                stdout=subprocess.PIPE,  # Capture stdout si nécessaire
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to mount volume '{name}': {e.stderr or e}")

    def unmount_volume(self, name: str):
        """
        Unmount a mounted Gocryptfs volume.

        Args:
            name (str): Name of the volume to unmount.

        Raises:
            FileNotFoundError: If the mount directory doesn't exist.
            RuntimeError: If the unmounting process fails.
        """
        mount_path = self.mount_dir / f"{name}"  # Path to the mount directory

        # Ensure the mount directory exists
        if not mount_path.exists():
            raise FileNotFoundError(f"Mount point '{name}' does not exist at {mount_path}.")

        try:
            # Unmount the Gocryptfs volume
            subprocess.run(
                ["fusermount", "-u", str(mount_path)],
                check=True,  # Automatically raise CalledProcessError on failure
                stderr=subprocess.PIPE,  # Capture stderr pour éviter qu'il ne s'affiche
                stdout=subprocess.PIPE,  # Capture stdout si nécessaire               
            )

            # Remove the mount directory after unmounting
            os.rmdir(mount_path)  # Attempt to remove the empty mount directory
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to unmount volume '{name}': {e.stderr or e}")
        except OSError as e:
            raise RuntimeError(f"Error removing mount directory '{mount_path}': {e}")


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
        password = "securepassword123"

        # Test 1: Simple volume creation
        # gocryptfs_tool.create_volume("test_volume_001", password)

        # # Test 2: Creating an already existing volume
        # gocryptfs_tool.create_volume("test_volume_001", password)

        # Test 3: Simple volume mounting
        # gocryptfs_tool.mount_volume("test_volume_001", password)

        # Test 4: Mounting a non-existing volume
        # gocryptfs_tool.mount_volume("non_existing_volume", password)
        
        # Test 5: Mounting a volume that's already mounted
        # gocryptfs_tool.mount_volume("test_volume_001", password)
        
        # Test 6: Simple volume unmounting
        # gocryptfs_tool.unmount_volume("test_volume_001")

        # Test 7: Unmounting a non-existing mount point
        # gocryptfs_tool.unmount_volume("non_existing_volume")

        # Test 8: Unmounting an already unmounted volume
        gocryptfs_tool.unmount_volume("test_volume_001")

    except Exception as e:
        print(e)
