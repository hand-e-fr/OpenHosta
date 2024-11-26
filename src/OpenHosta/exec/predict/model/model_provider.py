from typing import Optional, Literal, get_origin

from .builtins.classification import Classification
from .builtins.linear_regression import LinearRegression
from .hosta_model import HostaModel
from .neural_network import NeuralNetwork
from .neural_network_types import ArchitectureType
from ..predict_config import PredictConfig
from ....core.hosta import Func
from ....core.logger import Logger, ANSIColor
from ....utils.torch_nn_utils import type_size


class HostaModelProvider:
    @staticmethod
    def from_hosta_func(func: Func, config: Optional[PredictConfig], architecture: Optional[NeuralNetwork], path: str, logger: Logger) -> Optional[HostaModel]:
        input_size = 0
        for arg in func.f_type[0]:
            if get_origin(arg) is Literal:
                input_size += 1
            else:
                input_size += type_size(arg, config.max_tokens)

        output_size = type_size(func.f_type[1], config.max_tokens)
        logger.log_debug(f"Model with input size {input_size} and output size {output_size}", level=2)

        hosta_model: Optional[HostaModel] = None
        model_type = determine_model_type(func)

        if model_type == ArchitectureType.LINEAR_REGRESSION:
            hosta_model = LinearRegression(architecture, input_size, output_size, config, logger)

        elif model_type == ArchitectureType.CLASSIFICATION:
            hosta_model = Classification(architecture, input_size, output_size, config, logger)
        else:
            raise ValueError(f"Model type {model_type} not supported")

        logger.log_custom("Model", f"Type : {type(hosta_model).__name__}", color=ANSIColor.BLUE_BOLD)


        if architecture is None:
            save_architecture(hosta_model, path, logger)

        return hosta_model


def determine_model_type(func: Func) -> ArchitectureType:
    if get_origin(func.f_type[1]) is Literal:
        return ArchitectureType.CLASSIFICATION
    else:
        return ArchitectureType.LINEAR_REGRESSION


def save_architecture(hosta_model: HostaModel, path: str, logger : Logger):
    architecture = NeuralNetwork.from_torch_nn(hosta_model)
    with open(path, 'w', encoding='utf-8') as file:
        file.write(architecture.to_json())
    logger.log_custom("Architecture", f"saved to {path}", color=ANSIColor.BRIGHT_GREEN, level=2)