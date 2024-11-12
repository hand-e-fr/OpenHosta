from abc import ABC
from ..predict_memory import PredictMemory
from enum import Enum

from .builtins.classification import Classification
from .builtins.linear_regression import LinearRegression

class ArchitectureType(Enum):
    """
    Enum for different built-in architectures for neural networks.
    """
    LINEAR_REGRESSION = 1
    CLASSIFICATION = 2


class BaseArchitecture(ABC):

    def training(self, train_set, epochs, verbose):
        pass

    def validate(self, validation_set):
        pass

    def predict(self, test_set):
        pass

    def init_weights(self):
        pass

    def save_architecture(self, memory: PredictMemory):
        pass

    def from_hosta(self, func, model, path, verbose):
        if model is not None:
            if model.model_type == ArchitectureType.LINEAR_REGRESSION:
                architecture = LinearRegression()
                architecture = None
            elif model.model_type == ArchitectureType.CLASSIFICATION:
                architecture = Classification()
        architecture.to_json(path) #
        return architecture
