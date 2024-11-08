from enum import Enum
import json
import numpy as np
from .memory import HostaMemory
from typing import Optional, Dict, Any, NamedTuple
import os


File = NamedTuple("File", [("exist", bool), ("path", str), ("element", Any)])

class PredictFileType(Enum):
    """File types specific to prediction"""
    WEIGHTS = "weights.pth"
    ARCHITECTURE = "architecture.json"
    SUMMARY = "summary.txt"
    DATA_CSV = "data.csv"
    DATA_NPY = "data.npy"


class PredictMemory(HostaMemory):
    def __init__(self, base_path: Optional[str] = None, *, name: str = None, **kwargs):
        super().__init__(base_path=base_path, **kwargs)
        if name is None:
            raise ValueError("name must be specified")
        self.name = name
        self.paths: Dict[PredictFileType, str] = {}
        self.files: Dict[PredictFileType, File] = {}

    @staticmethod
    def loading(base_path: Optional[str] = None, *, name: str = None) -> 'PredictMemory':
        """Creates or loads a PredictMemory instance with all its files"""
        memory = PredictMemory(base_path=base_path, name=name)
        
        if not memory.files:
            memory._initialize_predict_directory
            for file_type in PredictFileType:
                memory.files[file_type] = memory._process_file(file_type)
        
        return memory

    def _process_file(self, file_type: PredictFileType) -> File:
        """Process a single file and return its File object"""
        path = self.paths[file_type]
        
        # Create file if it doesn't exist
        if not os.path.exists(path):
            self._create_empty_file(file_type)
            return File(exist=False, path=path, element=None)
        
        # Check if file has content
        is_not_empty = self._is_file_not_empty(file_type)
        content = self._read_file(file_type) if is_not_empty else None
        
        return File(exist=is_not_empty, path=path, element=content)

    def _is_file_not_empty(self, file_type: PredictFileType) -> bool:
        """Check if a file has content"""
        path = self.paths[file_type]
        if file_type in [PredictFileType.WEIGHTS, PredictFileType.DATA_NPY]:
            return os.path.getsize(path) > 0
        try:
            with open(path, 'r') as f:
                return len(f.read().strip()) > 0
        except Exception:
            return False

    def _read_file(self, file_type: PredictFileType) -> Any:
        """Read and return file content"""
        path = self.paths[file_type]
        try:
            if file_type == PredictFileType.ARCHITECTURE:
                with open(path, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        return {}
                    return json.loads(content)
            elif file_type == PredictFileType.DATA_NPY:
                return np.load(path)
            elif file_type in [PredictFileType.WEIGHTS]:
                with open(path, 'rb') as f:
                    return f.read()
            else:
                with open(path, 'r') as f:
                    return f.read()
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"Error reading {file_type.value}: JSON is invalid", path, 0)
        except Exception as e:
            print(f"Error reading {file_type.value}: {str(e)}")
            return None

    def _create_empty_file(self, file_type: PredictFileType) -> None:
        """Create an empty file with appropriate initial content"""
        path = self.paths[file_type]
        mode = 'wb' if file_type in [PredictFileType.WEIGHTS, PredictFileType.DATA_NPY] else 'w'
        
        with open(path, mode) as f:
            if file_type == PredictFileType.SUMMARY:
                f.write("=== Prediction Log Summary ===\n")
            elif file_type == PredictFileType.ARCHITECTURE:
                json.dump({}, f) 

    def update(self, file_type: PredictFileType, content: Any) -> None:
        """Update a file with new content"""
        path = self.paths[file_type]
        
        # Save content
        if file_type == PredictFileType.ARCHITECTURE:
            with open(path, 'w') as f:
                json.dump(content, f, indent=4)
        elif file_type == PredictFileType.DATA_NPY:
            np.save(path, content)
        elif file_type in [PredictFileType.WEIGHTS]:
            with open(path, 'wb') as f:
                f.write(content)
        else:
            with open(path, 'w') as f:
                f.write(str(content))
        
        self.files[file_type] = File(exist=True, path=path, element=content)

    @property
    def _initialize_predict_directory(self) -> None:
        """Initialize the prediction directory and file paths"""
        predict_dir = os.path.join(self.root, self.name)
        self._ensure_directory_exists(predict_dir)
        
        self.paths = {
            file_type: os.path.join(predict_dir, file_type.value)
            for file_type in PredictFileType
        }
    @property
    def weight(self) -> File:
        return self.files[PredictFileType.WEIGHTS]
    
    @property
    def architecture(self) -> File:
        return self.files[PredictFileType.ARCHITECTURE]
    
    @property
    def summary(self) -> File:
        return self.files[PredictFileType.SUMMARY]
    
    @property
    def data_csv(self) -> File:
        return self.files[PredictFileType.DATA_CSV]
    
    @property
    def data_npy(self) -> File:
        return self.files[PredictFileType.DATA_NPY]