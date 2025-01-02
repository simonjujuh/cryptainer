import os
import subprocess
from pathlib import Path
from cryptainer.volumes.base import VolumeTool


class GocryptfsTool(VolumeTool):

    def create_volume(self, path: str, password: str, size: str = None) -> str:
        volume_path = Path(path)

        # Check if the volume already exists
        if volume_path.exists():
            raise FileExistsError(f"Volume {volume_path} already exists")

        # Ensure the volume directory exists
        os.makedirs(volume_path)

        subprocess.run(
            ["gocryptfs", "-q", "-init", "-passfile", "/dev/stdin", str(volume_path)],
            input=password,  # Pass the password through stdin
            text=True,
            check=True,  # Automatically raise CalledProcessError on failure
            stderr=subprocess.PIPE,  # Capture stderr pour éviter qu'il ne s'affiche
            stdout=subprocess.PIPE,  # Capture stdout si nécessaire
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

        # Mount the Gocryptfs volume
        subprocess.run(
            ["gocryptfs", "-q", "-allow_other", "-passfile", "/dev/stdin", str(volume_path), str(mount_path)],
            input=password,  # Pass the password through stdin
            text=True,
            check=True,  # Automatically raise CalledProcessError on failure
            stderr=subprocess.PIPE,  # Capture stderr pour éviter qu'il ne s'affiche
            stdout=subprocess.PIPE,  # Capture stdout si nécessaire
        )

    def unmount_volume(self, mount_path: str):
        mount_path = Path(mount_path)  # Path to the mount directory

        # Ensure the mount directory exists
        if not mount_path.exists():
            raise FileNotFoundError(f"Path {mount_path} does not exist")

        # Unmount the Gocryptfs volume
        subprocess.run(
            ["fusermount", "-u", str(mount_path)],
            check=True,  # Automatically raise CalledProcessError on failure
            stderr=subprocess.PIPE,  # Capture stderr pour éviter qu'il ne s'affiche
            stdout=subprocess.PIPE,  # Capture stdout si nécessaire               
        )

        # Remove the mount directory after unmounting
        os.rmdir(mount_path)  # Attempt to remove the empty mount directory



if __name__ == "__main__":
    pass