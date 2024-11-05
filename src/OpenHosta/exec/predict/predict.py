import os
from typing import Union

from .data import PredictData
from .model_schema import ModelSchema
from .type_encoder.hosta_encoder import HostaEncoder
from .. import prefix
from ...core.hosta import Hosta, Func
from ...core.config import Model


class ConfigModel: # todo: change name
    def __init__(self, architecture: ModelSchema):
        self.architecture = architecture


class PredictBase:
    _instance = {}

    def __new__(cls, x: Hosta = None, model: ConfigModel = None, oracle: Union[Model, None] = None, verbose: bool = False):
        hosta_key = hash(x) # todo: change hash function

        if hosta_key not in cls._instance:
            if verbose:
                print(f"{prefix('predict')} Creating new instance of PredictBase")
            cls._instance[hosta_key] = super(PredictBase, cls).__new__(cls)
            try:
                setattr(cls._instance[hosta_key], '_initialized', False)
            except AttributeError:
                pass
        return cls._instance[hosta_key]

    def __init__(self, x: Hosta = None, model: ConfigModel = None, oracle: Union[Model, None] = None, verbose: bool = False):
        if not hasattr(self, '_initialized') or not getattr(self, '_initialized'):
            self._infos: Func = getattr(x, "_infos")
            if self._infos.f_type[1] is None:
                raise ValueError(f"Return type must be specified for the function")
            if self._infos.f_type[1] not in [int, float, bool]:
                raise ValueError(f"Return type must be one of [int, float, bool], not {self._infos.f_type[1]}")
            self._model: ConfigModel = model
            self._oracle: Union[Model, None] = oracle
            self._verbose: bool = verbose
            self._encoder: HostaEncoder = HostaEncoder()
            self._data: PredictData = PredictData(path=os.path.join(os.path.dirname(__file__), "__hostacache__", str(hash(x))))
            self._initialized: bool = True

    def predict(self) -> Union[int, float, bool]:
        """
        :return:
        """
        print("Args type:")
        for (_, t), (k, v) in zip(enumerate(self._infos.f_type[0]), self._infos.f_args.items()):
            print(f"{k}: {t} = {v}")
        print("Return type:")
        print(self._infos.f_type[1])
        print("Examples:")
        for ex in self._infos.f_mem:
            print(f"Input: {ex.value['in_']}, Output: {ex.value['out']}")
        return 0


def predict(model: ConfigModel = None, oracle: Union[Model, None] = None, verbose: bool = False) -> Union[int, float, bool]:
    if verbose:
        print(f"{prefix("predict")} Predicting...")
    x: Hosta = Hosta()
    predict_base = PredictBase(x=x, model=model, oracle=oracle, verbose=verbose)
    return predict_base.predict()
