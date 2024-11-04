import os
from typing import Union

from .cache import HostaModelData, ModelCachedData
from .type_encoder.hosta_encoder import HostaEncoder
from .. import prefix
from ...core.hosta import Hosta, Func
from ...core.config import Model


class ConfigArchitecture:
    def __init__(self, name: str, model_type: str, weight_path: str, version: str, complexity: float, epochs: int, batch_size: int, learning_rate: float, get_loss: float):
        self.name = name
        self.model_type = model_type
        self.weight_path = weight_path
        self.version = version
        self.complexity = complexity
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.get_loss = get_loss

class ConfigModel: # todo: change name
    def __init__(self, architecture: ConfigArchitecture):
        self.architecture = architecture

class PredictBase:
    def __init__(self, x: Hosta = None, verbose: bool = False):
        self._infos: Func = getattr(x, "_infos")
        self._encoder = HostaEncoder()

    def predict(self) -> Union[int, float, bool]:
        """
        :return:
        """
        print("Args type:")
        print("Args type:")
        for (_, t), (k, v) in zip(enumerate(self._infos.f_type[0]), self._infos.f_args.items()):
            print(f"{k}: {t} = {v}")
        print("Return type:")
        print(self._infos.f_type[1])
        pass

def predict(model: ConfigModel = None, oracle: Union[Model, None] = None, verbose: bool = False) -> Union[int, float, bool]:
    if (verbose):
        print(f"{prefix("predict")} Predicting...")
    x: Hosta = Hosta()
    predict_base = PredictBase(x=x, verbose=verbose)
    return predict_base.predict()
