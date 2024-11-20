from typing import Optional, Literal, get_origin

from torch.backends.mkl import verbose

from .builtins.classification import Classification
from .builtins.linear_regression import LinearRegression
from .hosta_model import HostaModel
from .neural_network import NeuralNetwork
from .neural_network_types import ArchitectureType
from ..predict_config import PredictConfig
from ....core.hosta import Func
from ....utils.torch_nn_utils import type_size
from ....core.logger import Logger, ANSIColor


class HostaModelProvider:
    @staticmethod
    def from_hosta_func(func: Func, config: Optional[PredictConfig], architecture: Optional[NeuralNetwork], path: str, logger: Logger) -> Optional[HostaModel]:
        input_size = 0

        for arg in func.f_type[0]:
            input_size += type_size(arg, config.max_tokens)

        output_size = type_size(func.f_type[1], config.max_tokens)
        hosta_model: Optional[HostaModel] = None

        logger.log_debug(f"Creating model with input size {input_size} and output size {output_size}", 2)

        if config is not None and config.model_type is not None:
            if config.model_type == ArchitectureType.LINEAR_REGRESSION:
                hosta_model = LinearRegression(architecture, input_size, output_size, config.complexity)
            elif config.model_type == ArchitectureType.CLASSIFICATION:
                hosta_model = Classification(architecture, input_size, output_size, config.complexity, 1, logger)
        else:
            if get_origin(func.f_type[1]) is Literal:
                hosta_model = Classification(architecture, input_size, output_size, config.complexity, 1, logger)
            else:
                hosta_model = LinearRegression(architecture, input_size, output_size, config.complexity, logger)

        logger.log_custom("Model", f"created, type : {type(hosta_model).__name__}", color=ANSIColor.BRIGHT_GREEN)

        with open(path, 'w') as file:
            file.write(NeuralNetwork.from_torch_nn(hosta_model).to_json())
        return hosta_model
