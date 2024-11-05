from typing import Union

from .architecture.builtins import ArchitectureType

class ModelSchema:
    def __init__(self,
                 model_type: ArchitectureType = ArchitectureType.LINEAR_REGRESSION,
                 name: str = "",
                 weight_path: str = "",
                 version: str = "",
                 complexity: Union[float, None] = None,
                 epochs: Union[int, None] = None,
                 batch_size: Union[int, None] = None,
                 learning_rate: Union[float, None] = None,
                 get_loss: Union[float, None] = None
             ):
        self.model_type: ArchitectureType = model_type

        self.name: str = name
        self.weight_path: str = weight_path
        self.version: str = version

        self.complexity: float = complexity

        if batch_size is None:
            self.batch_size: int = int(0.05 * len(train)) if 0.05 * len(train) > 1 else len(train) # 5% of the dataset or len(train) if len(train) <= 1
        else:
            self.batch_size: int = batch_size
        self.epochs: int = epochs
        self.learning_rate: float = learning_rate
        self.get_loss: float = get_loss

    def to_json(self):
        return f"""{{
            "name": "{self.name}",
            "model_type": "{self.model_type}",
            "weight_path": "{self.weight_path}",
            "version": "{self.version}",
            "complexity": {self.complexity},
            "epochs": {self.epochs},
            "batch_size": {self.batch_size},
            "learning_rate": {self.learning_rate},
            "get_loss": {self.get_loss}
        }}"""

    @staticmethod
    def from_json(json_str: str):
        import json
        data = json.loads(json_str)
        return ModelSchema(
            name=data["name"],
            model_type=ArchitectureType(data["model_type"]),
            weight_path=data["weight_path"],
            version=data["version"],
            complexity=data["complexity"],
            epochs=data["epochs"],
            batch_size=data["batch_size"],
            learning_rate=data["learning_rate"],
            get_loss=data["get_loss"]
        )