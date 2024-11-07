import os
from typing import Union, Tuple, Callable, Optional

from .cache import PredictCache
from .dataset.oracle import LLMSyntheticDataGenerator
from .encoder.simple_encoder import SimpleEncoder
from .model_schema import ModelSchema
from ...core.config import Model
from ...core.hosta import Hosta, Func


class ConfigModel: # todo: change name
    def __init__(self, architecture: ModelSchema):
        self.architecture = architecture


class PredictBase:
    _instance = {}

    def __new__(cls, x: Hosta = None, model: ConfigModel = None, oracle: Optional[Union[Model, Callable]] = None, verbose: bool = False):
        hosta_key = hash(x) # todo: change hash function

        if hosta_key not in cls._instance:
            if verbose:
                print(f"Creating new instance of PredictBase")
            cls._instance[hosta_key] = super(PredictBase, cls).__new__(cls)
            try:
                setattr(cls._instance[hosta_key], '_initialized', False)
            except AttributeError:
                pass
        return cls._instance[hosta_key]

    def __init__(self, x: Hosta = None, model: ConfigModel = None, oracle: Optional[Union[Model, Callable]] = None, verbose: bool = False):
        if not hasattr(self, '_initialized') or not getattr(self, '_initialized'):
            self.infos: Func = getattr(x, "_infos")
            assert self.infos, "Function must be provided."
            assert self.infos.f_type[1], "Return type must be specified for the function."
            assert self.infos.f_type[1] in [int, float, bool], f"Return type must be one of [int, float, bool], not {self.infos.f_type[1]}."

            self._model: ConfigModel = model
            self._verbose: bool = verbose
            self._encoder: SimpleEncoder = SimpleEncoder()
            self._data: PredictCache = PredictCache(path=os.path.join(os.path.dirname(__file__), "__hostacache__", str(hash(x))))
            self._initialized: bool = True
            self.oracle: Optional[Union[Model, Callable]] = oracle
            self.examples: dict[int, Tuple[list[Union[int, float, bool]], Union[int, float, bool]]] = {}

    def predict(self) -> Union[int, float, bool]:
        """
        :return:
        """
        return 0


def predict(model: ConfigModel = None, oracle: Optional[Model] = None, verbose: bool = False) -> Union[int, float, bool]:
    x: Hosta = Hosta()
    predict_base = PredictBase(x=x, model=model, oracle=oracle, verbose=verbose)
    LLMSyntheticDataGenerator.generate_synthetic_data(
        func=predict_base.infos,
        request_amounts=3,
        examples_in_req=50,
        model=None
    )
    return predict_base.predict()
