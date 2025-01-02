from abc import ABC, abstractmethod
from pathlib import Path

class VolumeTool(ABC):
    
    @abstractmethod
    def create_volume(self, path: str, password: str, size: str = None) -> str:
        pass

    @abstractmethod
    def mount_volume(self, volume_path: str, mount_path: str, password: str):
        pass

    @abstractmethod
    def unmount_volume(self, mount_path: str):
        pass



