import os
from typing import Union, Optional, Literal

from .model_schema import ConfigModel
from .dataset.dataset import HostaDataset, SourceType

from ...core.hosta import Hosta, Func
from ...core.config import Model, DefaultModel
from .predict_memory import PredictMemory
# from .architecture.builtins.linear_regression import LinearRegressionBuilder

# from .dataset.sample_type import Sample
# from .encoder.simple_encoder import SimpleEncoder

architectures_model = {
    "classification": "on classifie nous",
    "linear_regression": 'on fait une régression linéaire'
}

def predict(model: ConfigModel = None, oracle: Optional[Union[Model, HostaDataset]] = None, verbose: bool = False) -> Union[int, float, bool]:
    x: Hosta = Hosta()
    func: Func = getattr(x, "_infos")

    name = model.name if model is not None and model.name is not None else func.f_name
    base_path = model.path if model is not None and model.path is not None else os.getcwd()

    memory = PredictMemory.loading(base_path=base_path, name=name)
    print(func.f_args)
    dataset = HostaDataset.get_sample(func.f_args)
    print(dataset.inference)
    if memory.architecture.exist:
        print("architecture exist")
        print(memory.architecture)
    else :
        print("architecture not ready")
    
    return 0
    

from .dataset.oracle import LLMSyntheticDataGenerator
from .architecture.builtins.classification import ClassificationBuilder

def data_preparator(func: Func, memory: PredictMemory, oracle: Optional[Union[Model, HostaDataset]], model: Optional[ConfigModel]) -> HostaDataset:
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

        
    if func.f_type[1] == Literal or model is not None and model.arhitecture == ClassificationBuilder:
        classification = True
    else:
        classification = False

    dataset.encode(tokenizer=None, max_tokens=10, classification=classification)
    return dataset

