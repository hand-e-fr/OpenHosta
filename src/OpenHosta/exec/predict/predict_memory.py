import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict

from ...core.memory import HostaMemory


@dataclass
class File:
    exist: bool
    path: str


class PredictFileType(Enum):
    """Enumaration for different types of files in the prediction memory."""
    ARCHITECTURE = "model.json"
    WEIGHTS = "weights.pth"
    DICTIONARY = "dictionary.json"
    DATA = "data.json"
    SUMMARY = "summary.txt"
    NORMALIZATION = "normalization.json"


class PredictMemory(HostaMemory):
    """
    This module defines the PredictMemory class, which manages the structure of files for prediction purposes. 
    It inherits from HostaMemory, which handles the main cache directory.

    He uses the File structure to store the status of each file and his path.
    """

    def __init__(self, base_path: Optional[str] = None, *, name: str = None, **kwargs):
        super().__init__(base_path=base_path, **kwargs)
        if name is None:
            raise ValueError("name must be specified")
        self.name = name
        self.paths: Dict[PredictFileType, str] = {}
        self.files: Dict[PredictFileType, File] = {}

    @staticmethod
    def load(base_path: Optional[str] = None, name: str = None) -> 'PredictMemory':
        """
        Static method to create or load a memory.
        Args:
            base_path: Base path for the memory.
            name: Name of the memory.
        Returns:
            PredictMemory instance.
        """
        memory = PredictMemory(base_path=base_path, name=name)
        memory._initialize_predict_directory()
        memory._check_files()
        return memory

    def _initialize_predict_directory(self) -> None:
        """
        Initializes the directory and file structure for predictions.
        """
        self.predict_dir = os.path.join(self.cache_root, self.name)
        self._ensure_directory_exists(self.predict_dir)
        self.paths = {
            file_type: os.path.join(self.predict_dir, file_type.value)
            for file_type in PredictFileType
        }

    def _check_files(self) -> None:
        """
        Checks the status of all files.
        """
        for file_type in PredictFileType:
            path = self.paths[file_type]
            exists = os.path.exists(path) and os.path.getsize(path) > 0
            self.files[file_type] = File(exist=exists, path=path)

    @property
    def architecture(self) -> File:
        return self.files[PredictFileType.ARCHITECTURE]

    @property
    def weights(self) -> File:
        return self.files[PredictFileType.WEIGHTS]

    @property
    def data(self) -> File:
        return self.files[PredictFileType.DATA]

    @property
    def summary(self) -> File:
        return self.files[PredictFileType.SUMMARY]

    @property
    def dictionary(self) -> File:
        return self.files[PredictFileType.DICTIONARY]

    @property
    def normalization(self) -> File:
        return self.files[PredictFileType.NORMALIZATION]
