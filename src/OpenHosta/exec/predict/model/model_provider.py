from enum import Enum
from typing import Optional

from .builtins.classification import Classification
from .builtins.linear_regression import LinearRegression
from .hosta_model import HostaModel
from .neural_network import NeuralNetwork
from ..config_model import ConfigModel
from ....utils.torch_nn_utils import type_size


class HostaModelProvider:
    @staticmethod
    def from_hosta_func(func, model: ConfigModel, path, verbose):
        input_size = type_size(func.f_type[0])
        output_size = type_size(func.f_type[1])
        architecture: Optional[HostaModel] = None

        with open(path, 'r') as file:
            file_content = file.read()
        cached_architecture = NeuralNetwork.from_json(file_content)

        if model is not None and model.model_type is not None:
            if model.model_type == ArchitectureType.LINEAR_REGRESSION:
                architecture = LinearRegression(cached_architecture, input_size, output_size, model.complexity)
            elif model.model_type == ArchitectureType.CLASSIFICATION:
                architecture = Classification(cached_architecture, input_size, output_size, model.complexity)
        else:
            architecture = LinearRegression(cached_architecture, input_size, output_size, model.complexity)

        with open(path, 'w') as file:
            file.write(NeuralNetwork.from_torch_nn(architecture).to_json())
        return architecture
