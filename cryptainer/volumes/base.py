from abc import ABC, abstractmethod
from pathlib import Path

class VolumeTool(ABC):
    def __init__(self, volume_dir: str, mount_dir: str):
        self.volume_dir = Path(volume_dir)
        self.mount_dir = Path(mount_dir)

    @abstractmethod
    def create_volume(self, name: str, password: str, size: str = None) -> str:
        pass

    @abstractmethod
    def mount_volume(self, name: str, password: str):
        pass

    @abstractmethod
    def unmount_volume(self, name: str):
        pass



