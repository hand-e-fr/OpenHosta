import os
from typing import Union

from .. import prefix
from .config import PredictConfig
from .cache import HostaModelCache, ModelCachedData
from .type_encoder.hosta_encoder import HostaEncoder
from ...core.hosta import Hosta, Func

class PredictBase:
    def __init__(self, x: Hosta = None, verbose: bool = False):
        self._infos: Func = getattr(x, "_infos")
        self._cached_data = ModelCachedData()
        self._cache_provider = HostaModelCache(
            hash_key="example_key",
            data=self._cached_data,
            verbose=verbose
        )
        self._weight_path = os.path.join(self._cache_provider.folder_path(), "model.pth")
        self._encoder = HostaEncoder()

    def predict(self, config: PredictConfig) -> Union[int, float, bool]:
        """
        :return:
        """

        pass

def predict(config: PredictConfig = None, verbose: bool = False) -> Union[int, float, bool]:
    if (verbose):
        print(f"{prefix("predict")} Predicting...")
    x: Hosta = Hosta()
    predict_base = PredictBase(x=x, verbose=verbose)
    if config is None:
        config = PredictConfig()
    return predict_base.predict(config)
