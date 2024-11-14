from typing import Optional, Literal, get_origin
from numpy.ma.extras import mr_class

from .builtins.classification import Classification
from .builtins.linear_regression import LinearRegression
from .hosta_model import HostaModel
from .neural_network_types import ArchitectureType
from .neural_network import NeuralNetwork
from ..predict_config import PredictConfig
from ..predict_memory import PredictMemory, File
from ....core.hosta import Func
from ....utils.torch_nn_utils import type_size


class HostaModelProvider:
    @staticmethod
    def from_hosta_func(func: Func, config: Optional[PredictConfig], architecture: Optional[NeuralNetwork], path: str, verbose: int) -> Optional[HostaModel]:
        input_size = type_size(func.f_type[0], config.max_tokens)
        output_size = type_size(func.f_type[1], config.max_tokens)
        hosta_model: Optional[HostaModel] = None
        if config is not None and config.model_type is not None:
            if config.model_type == ArchitectureType.LINEAR_REGRESSION:
                hosta_model = LinearRegression(architecture, input_size, output_size, config.complexity)
            elif config.model_type == ArchitectureType.CLASSIFICATION:
                hosta_model = Classification(architecture, input_size, output_size, config.complexity, 1)
        else:
            if get_origin(func.f_type[1]) == Literal:
                hosta_model = Classification(architecture, input_size, output_size, 4, 1)
            else:
                hosta_model = LinearRegression(architecture, input_size, output_size, 4)

        with open(path, 'w') as file:
            file.write(NeuralNetwork.from_torch_nn(hosta_model).to_json())
        return hosta_model
