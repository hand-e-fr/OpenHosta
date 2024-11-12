from abc import ABC
from ..predict_memory import PredictMemory
from enum import Enum

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
