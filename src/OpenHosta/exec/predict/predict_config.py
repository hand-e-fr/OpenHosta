from typing import Optional

from .model.neural_network_types import ArchitectureType


class PredictConfig:
    def __init__(self,
                 model_type: ArchitectureType = None,
                 name: str = None,
                 path: str = None,
                 version: str = None,
                 complexity: int = 4,
                 max_tokens: int = 10,
                 epochs: Optional[int] = None,
                 batch_size: Optional[int] = None,
                 learning_rate: Optional[float] = None,
                 get_loss: Optional[float] = None,
                 dataset_path: Optional[str] = None
             ):
        self.model_type: ArchitectureType = model_type

        self.name: str = name
        self.path: str = path
        self.version: str = version

        self.complexity: int = complexity
        self.max_tokens: int = max_tokens

        self.batch_size: int = batch_size
        self.epochs: int = epochs
        self.learning_rate: float = learning_rate
        self.get_loss: float = get_loss
        self.dataset_path: str = dataset_path

    def to_json(self):
        return f"""{{
            "name": "{self.name}",
            "model_type": "{self.model_type}",
            "weight_path": "{self.path}",
            "version": "{self.version}",
            "complexity": {self.complexity},
            "max_tokens": {self.max_tokens},
            "epochs": {self.epochs},
            "batch_size": {self.batch_size},
            "learning_rate": {self.learning_rate},
            "get_loss": {self.get_loss},
            "dataset_path": "{self.dataset_path}",
        }}"""

    @staticmethod
    def from_json(json_str: str):
        import json
        data = json.loads(json_str)
        return PredictConfig(
            name=data["name"],
            model_type=ArchitectureType(data["model_type"]),
            path=data["path"],
            version=data["version"],
            complexity=data["complexity"],
            max_tokens=data["max_tokens"],
            epochs=data["epochs"],
            batch_size=data["batch_size"],
            learning_rate=data["learning_rate"],
            get_loss=data["get_loss"],
            dataset_path=data["dataset_path"],
        )
