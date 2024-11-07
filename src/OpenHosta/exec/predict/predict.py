import os
from typing import Union, Optional, Literal

from src.OpenHosta.core.config import DefaultModel
from .memory import PredictMemory
from .dataset.dataset import HostaDataset, SourceType
from .dataset.oracle import LLMSyntheticDataGenerator
from .dataset.sample_type import Sample
from .encoder.simple_encoder import SimpleEncoder
from .model_schema import ConfigModel
from ...core.config import Model
from ...core.hosta import Hosta, Func


def predict(model: ConfigModel = None, oracle: Optional[Union[Model, HostaDataset]] = None, verbose: bool = False) -> Union[int, float, bool]:
    x: Hosta = Hosta()
    func: Func = getattr(x, "_infos")

    encoder: SimpleEncoder = SimpleEncoder()
    memory: PredictMemory = PredictMemory(path=os.path.join(os.path.dirname(__file__), "__hostacache__", str(Hosta.hash_func(func))))
    dataset: HostaDataset = data_scientist(func=func, memory=memory, oracle=oracle, model=model)
          
    
    print(f"len: {len(dataset.data)}")
    print("inférence sample")

    inf = Sample(x.infos.f_args)
    print(inf)

    return 0 # todo: return the prediction




def data_scientist(func: Func, memory: PredictMemory, oracle: Optional[Union[Model, HostaDataset]], model: Optional[ConfigModel]) -> HostaDataset:
    """
    This function is used to generate the dataset for the model.
    he works like a data scientist, make a iterative process of each step automatically.
    Args:
        :param func: The function to analyze
        :param memory: The memory of the prediction
        :param oracle: The model to use to generate the dataset
        :param model: The model configuration
    Returns:
        :rtype: HostaDataset: The dataset generated
    """
    dataset: Optional[HostaDataset] = None

    if oracle is None and memory.data_path is not None and os.path.exists(memory.data_path) and os.path.isfile(memory.data_path) and os.path.getsize(memory.data_path) > 0:
        dataset = HostaDataset.from_source(memory.data_path, SourceType.CSV)
    elif oracle is None or isinstance(oracle, Model):
        dataset = LLMSyntheticDataGenerator.generate_synthetic_data(
            func=func,
            request_amounts=3, # todo: make it a parameter
            examples_in_req=50, # todo: make it a parameter
            model=oracle if oracle is not None else DefaultModel().get_default_model()
        )
        dataset.save(memory.data_path, SourceType.CSV)
    if func.f_type[1] == Literal:
        classification = True
    else:
        classification = False

    # dataset.encode(encoder=SimpleEncoder(), tokenizer=None, max_tokens=10, classification=classification)
    return dataset