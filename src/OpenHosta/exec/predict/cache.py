from typing import Any, Literal

from ...core.cache import HostaCache

class ModelCachedData:
    def __init__(
        self,
        weight_type: Any = None,
        loss_method: Literal["MSE", "CrossEntropy", "BCE"] = None,
        loss_sum: float = 0.0,
        optimizer: Literal["Adam", "SGD", "RMSprop", "AdamW"] = None,
        learning_rate: float = 0.0,
        epochs: int = 0,
        batch_size: int = 0
    ):
        self.weight_type = weight_type
        self.loss_method = loss_method
        self.loss_sum = loss_sum
        self.optimizer = optimizer
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size


class HostaModelCache(HostaCache[ModelCachedData]):
    @property
    def data_class(self):
        return ModelCachedData
