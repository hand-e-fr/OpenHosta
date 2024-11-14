from typing import Optional, Literal
import typing
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
    def from_hosta_func(func: Func, model: Optional[PredictConfig], architecture: Optional[NeuralNetwork], path: str, verbose: int) -> Optional[HostaModel]:
        input_size = type_size(func.f_type[0])
        output_size = type_size(func.f_type[1])
        hosta_model: Optional[HostaModel] = None
        complexity: int = model.complexity if model is not None and model.complexity is not None else 4
        print("here 1 ")
        if model is not None and model.model_type is not None:
            if model.model_type == ArchitectureType.LINEAR_REGRESSION:
                hosta_model = LinearRegression(architecture, input_size, output_size, complexity)
                print("here 1.1")
            elif model.model_type == ArchitectureType.CLASSIFICATION:
                print("here 1.2")
                hosta_model = Classification(architecture, input_size, output_size, complexity, 1)
            print("here 2")
        else:
            print(f"Model type is : {type(func.f_type[1])}")
            if getattr(func.f_type[1], '__origin__', None) is typing.Literal :
                print("Output type is Literal, defaulting to classification")
                hosta_model = Classification(architecture, input_size, output_size, complexity, 1)
            else:
                print("Output type is not Literal, defaulting to linear regression")
                hosta_model = LinearRegression(architecture, input_size, output_size, complexity)

        with open(path, 'w') as file:
            file.write(NeuralNetwork.from_torch_nn(hosta_model).to_json())
        return hosta_model
