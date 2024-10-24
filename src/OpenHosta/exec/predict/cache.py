from typing import Any, Literal

from ...core.cache import HostaCache

class ModelCachedData:
    def __init__(
        self,
        weight_type: Any = None,
        loss: Literal["MSE", "CrossEntropy", "BCE"] = None,
        optimizer: Literal["Adam", "SGD", "RMSprop", "AdamW"] = None,
        learning_rate: float = None,
        epochs: int = None,
        batch_size: int = None,
        loss_sum: int = None
    ):
        self.weight_type = weight_type
        self.loss = loss
        self.optimizer = optimizer
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.loss_sum = loss_sum

class HostaModelCache(HostaCache[ModelCachedData]):
    @property
    def data_class(self):
        return ModelCachedData
