import os
from typing import Optional

class HostaMemory:
    """
    Base class for persistent memory management.
    """
    _instances = {}
    CACHE_DIR = "__hostacache__"
    
    def __init__(self, base_path: Optional[str] = None, **kwargs):
        pass

    def __new__(cls, base_path: Optional[str] = None, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(HostaMemory, cls).__new__(cls)
            cls._instances[cls]._initialized = False
        if base_path is not None and not cls._instances[cls]._initialized:
            cls._instances[cls]._initialize(base_path)
        return cls._instances[cls]
    
    def _initialize(self, base_path: str) -> None:
        """Initializes the hostacache directory"""
        self.cache_root = os.path.join(base_path, self.CACHE_DIR)
        self._initialized = True
        self._ensure_directory_exists(self.cache_root)


    def _ensure_directory_exists(self, directory) -> None:
        """Creates the base directory if necessary"""
        if not os.path.exists(directory):
            os.makedirs(directory)