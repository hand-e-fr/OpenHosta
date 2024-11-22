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
        logger.log_debug(f"Creating model with input size {input_size} and output size {output_size}", 2)

        hosta_model: Optional[HostaModel] = None
        model_type = determine_model_type(func, config)

        if model_type == ArchitectureType.LINEAR_REGRESSION:
            hosta_model = LinearRegression(architecture, input_size, output_size, config.complexity)

        elif model_type == ArchitectureType.CLASSIFICATION:
            num_classes = 2 if output_size == 2 else 1
            hosta_model = Classification(architecture, input_size, output_size, config.complexity, num_classes, logger)
        else:
            raise ValueError(f"Model type {model_type} not supported")

        logger.log_custom("Model", f"created, type : {type(hosta_model).__name__}", color=ANSIColor.BRIGHT_GREEN)


        if architecture is None:
            save_architecture(hosta_model, path, logger)
        # with open(path, 'w') as file:
        #     file.write(NeuralNetwork.from_torch_nn(hosta_model).to_json())
        return hosta_model


def determine_model_type(func: Func, config : Optional[PredictConfig]) -> ArchitectureType:
    if config is not None and config.model_type is not None:
        return config.model_type
    else:
        if get_origin(func.f_type[1]) is Literal:
            return ArchitectureType.CLASSIFICATION
        else:
            return ArchitectureType.LINEAR_REGRESSION


def save_architecture(hosta_model: HostaModel, path: str, logger : Logger):
    architecture = NeuralNetwork.from_torch_nn(hosta_model)
    with open(path, 'w') as file:
        file.write(architecture.to_json())
    logger.log_custom("Architecture", f"saved to {path}", color=ANSIColor.BRIGHT_GREEN)