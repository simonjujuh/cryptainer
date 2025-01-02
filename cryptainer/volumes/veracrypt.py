import os
import subprocess
from pathlib import Path
from cryptainer.volumes.base import VolumeTool


class VeraCryptTool(VolumeTool):

    def create_volume(self, path: str, password: str, size: str = '1024M') -> str:
        volume_path = Path(path)

        # Check if the volume already exists
        if volume_path.exists():
            raise FileExistsError(f"Volume {volume_path} already exists")

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

    def mount_volume(self, volume_path: str, mount_path: str, password: str):
        volume_path = Path(volume_path)  # Path to the encrypted volume
        mount_path = Path(mount_path)  # Directory to mount the volume

        # Ensure the volume exists
        if not volume_path.exists():
            raise FileNotFoundError(f"Volume {volume_path} does not exist")

        # Ensure the mount directory exists
        if mount_path.exists():
            raise FileExistsError(f"Target directory {mount_path} already exists")
        
        os.makedirs(mount_path)

        # Run the VeraCrypt command to mount the volume
        subprocess.run(
            [
                "veracrypt", "--text", "--mount", str(volume_path), str(mount_path),
                "--password", password, "--pim", "0", "--keyfiles", "", "--protect-hidden", "no"
            ],
            check=True,
        )
        
    def unmount_volume(self, mount_path: str):
        mount_path = Path(mount_path)  # Path to the mount directory

        # Ensure the mount directory exists
        if not mount_path.exists():
            raise FileNotFoundError(f"Path {mount_path} does not exist")

        # Run the VeraCrypt command to unmount the volume
        subprocess.run(
            ["veracrypt", "--text", "--dismount", str(mount_path)],
            check=True,
        )

        # Remove the mount directory after unmounting
        os.rmdir(mount_path)  # Attempt to remove the empty mount directory


if __name__ == "__main__":
    pass