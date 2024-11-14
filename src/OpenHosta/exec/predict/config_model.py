from typing import Optional

from .model.neural_network_types import ArchitectureType


class ConfigModel:
    def __init__(self,
                 model_type: ArchitectureType = None,
                 name: str = None,
                 path: str = None,
                 version: str = None,
                 complexity: Optional[float] = None,
                 epochs: Optional[int] = None,
                 batch_size: Optional[int] = None,
                 learning_rate: Optional[float] = None,
                 get_loss: Optional[float] = None,
                 dataset_path: Optional[str] = None,
             ):
        self.model_type: ArchitectureType = model_type

        self.name: str = name
        self.path: str = path
        self.version: str = version

        self.complexity: float = complexity

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
            "epochs": {self.epochs},
            "batch_size": {self.batch_size},
            "learning_rate": {self.learning_rate},
            "get_loss": {self.get_loss},
            "dataset_path": "{self.dataset_path}"
        }}"""

    @staticmethod
    def from_json(json_str: str):
        import json
        data = json.loads(json_str)
        return ConfigModel(
            name=data["name"],
            model_type=ArchitectureType(data["model_type"]),
            path=data["path"],
            version=data["version"],
            complexity=data["complexity"],
            epochs=data["epochs"],
            batch_size=data["batch_size"],
            learning_rate=data["learning_rate"],
            get_loss=data["get_loss"],
            dataset_path=data["dataset_path"]

        )
    



class New_Config_Model:
    archi_type: ArchitectureType
    archi_complexity: int
    archi_name: str
    archi_version: float
    train_epochs: int
    train_batch_size: int
    train_learning_rate: float
    train_get_loss: float
    data_path: str
    data_validation: bool # val_set or no
    