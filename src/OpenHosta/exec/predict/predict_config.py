from typing import Optional


class PredictConfig:
    def __init__(self,
                 name: str = None,
                 path: str = None,
                 complexity: int = 5,
                 growth_rate: float = 1.5,
                 coef_layers : int = 100,
                 normalize: bool = False,
                 epochs: Optional[int] = None,
                 batch_size: Optional[int] = None,
                 max_tokens: int = 1,
                 dataset_path: Optional[str] = None,
                 generated_data: Optional[int] = 100,
                ):
        self.name: str = name
        self.path: str = path
        self.complexity: int = complexity
        self.growth_rate: float = growth_rate
        self.coef_layers: int = coef_layers
        self.normalize: bool = normalize
        self.epochs: int = epochs
        self.batch_size: int = batch_size
        self.max_tokens: int = max_tokens
        self.dataset_path: str = dataset_path
        self.generated_data: int = generated_data

    def to_json(self):
        return f"""{{
            "name": "{self.name}",
            "path": "{self.path}",
            "complexity": {self.complexity},
            "growth_rate": {self.growth_rate},
            "coef_layers": {self.coef_layers},
            "normalize": {self.normalize},
            "epochs": {self.epochs},
            "batch_size": {self.batch_size},
            "max_tokens": {self.max_tokens},
            "dataset_path": "{self.dataset_path}",
            "generated_data": {self.generated_data}
        }}"""

    @staticmethod
    def from_json(json_str: str):
        import json
        data = json.loads(json_str)
        return PredictConfig(
            name=data["name"],
            path=data["path"],
            complexity=data["complexity"],
            growth_rate=data["growth_rate"],
            coef_layers=data["coef_layers"],
            normalize=data["normalize"],
            epochs=data["epochs"],
            batch_size=data["batch_size"],
            max_tokens=data["max_tokens"],
            dataset_path=data["dataset_path"],
            generated_data=data["generated_data"]
        )
