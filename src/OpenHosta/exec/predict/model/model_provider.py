from typing import Optional

from numpy.ma.extras import mr_class

from .builtins.classification import Classification
from .builtins.linear_regression import LinearRegression
from .hosta_model import HostaModel
from .neural_network_types import ArchitectureType
from .neural_network import NeuralNetwork
from ..config_model import ConfigModel
from ..predict_memory import PredictMemory, File
from ....core.hosta import Func
from ....utils.torch_nn_utils import type_size


class HostaModelProvider:
    @staticmethod
    def from_hosta_func(func: Func, model: Optional[ConfigModel], architecture: Optional[NeuralNetwork], path: str, verbose: int) -> Optional[HostaModel]:
        input_size = type_size(func.f_type[0])
        output_size = type_size(func.f_type[1])
        hosta_model: Optional[HostaModel] = None
        complexity: int = 44

        if model is not None and model.model_type is not None:
            if model.model_type == ArchitectureType.LINEAR_REGRESSION:
                hosta_model = LinearRegression(architecture, input_size, output_size, complexity)
            elif model.model_type == ArchitectureType.CLASSIFICATION:
                hosta_model = Classification(architecture, input_size, output_size, complexity)
        else:
            hosta_model = LinearRegression(architecture, input_size, output_size, complexity)

        with open(path, 'w') as file:
            file.write(NeuralNetwork.from_torch_nn(hosta_model).to_json())
        return hosta_model
