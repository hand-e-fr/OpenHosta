from enum import Enum
import json
import numpy as np
from ...core.memory import HostaMemory
from typing import Optional, Dict, Any, NamedTuple
import os


# 1. Structures de base
File = NamedTuple("File", [("exist", bool), ("path", str)])

class PredictFileType(Enum):
    """Enumaration for different types of files in the prediction memory."""
    ARCHITECTURE = "architecture.json"
    WEIGHTS = "weights.pth"
    DICTIONNARY = "dictionnary.txt"
    DATA = "data."
    SUMMARY = "summary.txt"

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
        memory._initialize_predict_directory
        memory._check_files()
        return memory

    @property
    def _initialize_predict_directory(self) -> None:
        """
        Initializes the directory and file structure for predictions.
        """
        predict_dir = os.path.join(self.cache_root, self.name)
        self._ensure_directory_exists(predict_dir)
        self.paths = {
            file_type: os.path.join(predict_dir, file_type.value)
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

    # def update(self, file_type: PredictFileType, content: Any) -> None:
    #     """
    #     Met à jour un fichier avec un nouveau contenu.
    #     Process:
    #     1. Récupère le chemin du fichier
    #     2. Écrit le contenu selon le type:
    #        - Binaire pour weights
    #        - JSON pour architecture
    #        - Texte pour les autres
    #     3. Met à jour l'état du fichier
    #     """
    #     path = self.paths[file_type]
    #     try:
    #         if file_type in [PredictFileType.WEIGHTS]:
    #             with open(path, 'wb') as f:
    #                 f.write(content)
    #         else:
    #             with open(path, 'w') as f:
    #                 if file_type == PredictFileType.ARCHITECTURE:
    #                     json.dump(content, f, indent=4)
    #                 else:
    #                     f.write(str(content))
    #         self.files[file_type] = File(exist=True, path=path)
    #     except Exception as e:
    #         print(f"Error updating {file_type.value}: {str(e)}")

    @property
    def architecture(self) -> File: return self.files[PredictFileType.ARCHITECTURE]

    @property
    def weights(self) -> File: return self.files[PredictFileType.WEIGHTS]

    @property
    def data(self) -> File: return self.files[PredictFileType.DATA]

    @property
    def summary(self) -> File: return self.files[PredictFileType.SUMMARY]

    @property
    def dictionnary(self) -> File: return self.files[PredictFileType.DICTIONNARY]
