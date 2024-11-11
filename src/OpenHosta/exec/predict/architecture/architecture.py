from typing import Union

from ....core.hosta import Func

from .neural_network import NeuralNetwork
from architecture.builtins.linear_regression import LinearRegressionBuilder
from architecture.builtins.classification import ClassificationBuilder
LINEAR_REGRESSION = "linear_regression"
CLASSIFICATION = "classification"

class Architecture(NeuralNetwork):
    def __init__():
        super().__init__()

    @staticmethod
    def get_architecture(func: Func, archi: Union[LinearRegressionBuilder, ClassificationBuilder] = None):
        """
        Get the architecture of the neural network for the given function.
        """
    pass