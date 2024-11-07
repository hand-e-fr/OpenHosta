import os
from typing import Union, Tuple, Callable, Optional, Literal

from .data import PredictData
from .model_schema import ConfigModel
from .dataset.dataset import HostaDataset
from .encoder.simple_encoder import SimpleEncoder
from .model_schema import ModelSchema
from ...core.config import Model
from ...core.hosta import Hosta, Func
from ...core.config import Model
from .dataset.sample_type import Sample


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
            self._infos: Func = getattr(x, "_infos")
            if self._infos.f_type[1] is None:
                raise ValueError(f"Return type must be specified for the function")
            # if self._infos.f_type[1] not in [int, float, bool]:
            #     raise ValueError(f"Return type must be one of [int, float, bool], not {self._infos.f_type[1]}")
            self._model: ConfigModel = model
            self._verbose: bool = verbose
            self._encoder: SimpleEncoder = SimpleEncoder()
            self._data: PredictCache = PredictCache(path=os.path.join(os.path.dirname(__file__), "__hostacache__", str(hash(x))))
            self._initialized: bool = True
            self.oracle: Optional[Union[Model, Callable]] = oracle
            self.examples: dict[int, Tuple[list[Union[int, float, bool]], Union[int, float, bool]]] = {}
            # for ex in self._infos.f_mem:
            #     self.examples[ex.id] = (list(ex.value["in_"].values()), ex.value["out"])

    def predict(self) -> Union[int, float, bool]:
        """
        :return:
        """
        return 0


def predict(model: ConfigModel = None, oracle: Optional[Model] = None, verbose: bool = False) -> Union[int, float, bool]:
    x: Hosta = Hosta()
    print(x._infos.f_args)
    print("*"*100)
    print(model.name)
    print("*"*100)
    # print(model.dataset_path)
    memory = ...
    if not memory.compilation : # fact that the function has been compiled and not changed and all the file are her
        dataset = data_scientist(hosta=x, model=model, oracle=oracle)
          
    
    print(len(dataset.data))
    print("inférence sample")

    inf = Sample(x.infos.f_args)
    print(inf)
    predict_base = PredictBase(x=x, model=model, oracle=oracle, verbose=verbose)
    LLMSyntheticDataGenerator.generate_synthetic_data(
        func=predict_base.infos,
        request_amounts=3,
        examples_in_req=50,
        model=None
    )
    return predict_base.predict()




def data_scientist(hosta : Hosta = None ,model: ConfigModel = None, oracle: Optional[Model] = None) -> HostaDataset:
    """
    This function is used to generate the dataset for the model.
    he works like a data scientist, make a iterative process of each step automatically.
    Args:
        hosta: The hosta function
        model: The model configuration
        oracle: The oracle model
    Returns:
        HostaDataset: An instance of the class that contains the dataset
    """
    if model.dataset_path is not None:
        dataset = HostaDataset.from_source(model.dataset_path)
        dataset.from_source(model.dataset_path)
        # for sample in dataset.data:
            # print(sample)
        # print(dataset.data)
    else:
        dataset = HostaDataset.generate(model=oracle, n_samples=100)
        # for sample in dataset.data:
            # print(sample)
    
    if hosta.infos.f_type[1] == Literal:
        classification = True
    else:
        classification = False

    dataset.encode(encoder=SimpleEncoder(), tokenizer=None, max_tokens=10, classification=classification)
    return dataset