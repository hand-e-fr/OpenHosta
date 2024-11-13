import os
from typing import Union, Optional

import torch

from .dataset.dataset import HostaDataset, SourceType
from .dataset.oracle import LLMSyntheticDataGenerator
from .model import HostaModel
from .model.model_provider import HostaModelProvider
from .config_model import ConfigModel
from .predict_memory import PredictMemory, File
from .model.neural_network import NeuralNetwork
from ...core.config import Model, DefaultModel
from ...core.hosta import Hosta, Func

def predict(
    model: ConfigModel = None,
    oracle: Optional[Union[Model, HostaDataset]] = None, #TODO: function for creating data (call a subclass of oracle ?)
    verbose: bool = False
) -> Union[int, float, bool, str]:
    """
    Predicts a result using an existing model or by creating a new one.
    
    Args:
        model: Model configuration
        oracle: Reference model or dataset for data generation
        verbose: Enables detailed logging
    
    Returns:
        Model prediction
    """
    func: Func = getattr(Hosta(), "_infos")

    name = model.name if model and model.name else func.f_name #TODO: add hash of args into the name of the func
    base_path = model.path if model and model.path else os.getcwd()
    memory : PredictMemory = PredictMemory.load(base_path=base_path, name=name)

    dataset : HostaDataset = None
    
    hosta_model : HostaModel = get_hosta_model(memory.architecture, func, model)
    architecture = None
    if not load_weights(memory, hosta_model):
        train_model(model, memory, hosta_model, dataset, oracle, func)
    
    if dataset is None:
        inference = HostaDataset.from_input(func.f_args, memory, verbose) # Pour le dictionnaire on envoie memory.dictionnary
    else:
        inference = dataset.prepare_input(func.f_args)
    
    # prediction = architecture.inference(inference)

    # return prediction
    return 0


def get_hosta_model(architecture_file: File, func: Func, model: Optional[ConfigModel] = None, verbose: int = 2) -> HostaModel:
    """
    Load or create a new model.
    """
    if verbose > 0:
        print("Loading model")
    architecture: Optional[NeuralNetwork] = None
    if architecture_file.exist:
        with open(architecture_file.path, "r") as file:
            json = file.read()
        architecture = NeuralNetwork.from_json(json)
        if verbose > 0:
            print(f"Model loaded from {architecture_file.path}")
        if verbose > 1:
            architecture.summary()
    return HostaModelProvider.from_hosta_func(func, model, architecture, architecture_file.path, verbose)


def load_weights(memory: PredictMemory, hosta_model: HostaModel) -> bool:
    """
    Load weights if they exist.
    """
    if memory.weights.exist:
        print("Loading weights")
        hosta_model.load_state_dict(torch.load(memory.weights.path, weights_only=True, map_location=hosta_model.device))
        hosta_model.eval()
        return True
    print("Weights not found")
    print(memory.weights.path)
    return False 


def train_model(model: ConfigModel, memory: PredictMemory, architecture: HostaModel, dataset: HostaDataset, oracle: Optional[Union[Model, HostaDataset]], func: Func, verbose: bool) -> None:
    """
    Prepare the data and train the model.
    """
    if memory.data.exist:
        train_set, val_set = HostaDataset.from_data(memory.data.path, verbose) # verbose will prcess all the example and add it to val_set
    else:
        train_set, val_set = prepare_dataset(model, memory, dataset, func, oracle, verbose)
    
    architecture.training(train_set, epochs=model.epochs) # verif le model epochs....
    
    if verbose:
        architecture.eval(val_set) # or directly in the training method at the end idk me fuck
    
    architecture.save_weights(memory.weights.path)


def prepare_dataset(model: ConfigModel, memory: PredictMemory, dataset: HostaDataset, func: Func, oracle: Optional[Union[Model, HostaDataset]], verbose: bool) -> tuple:
    """
    Prepare the dataset for training.
    """
    if model.dataset_path is not None:
        dataset = HostaDataset.from_files(model.dataset_path, SourceType.CSV, verbose) # or JSONL jsp comment faire la détection la
    else :
        print("generate Data")
        dataset = generate_data(memory, func, oracle, verbose)
        dataset.save(os.path.join(memory.predict_dir, "dataset.csv"), SourceType.CSV)
    print("encode data")
    dataset.encode(max_tokens=10, inference=False)
    print("FINISH")
    print(dataset.data)
    
    return "FINISH"
    if model.normalize:
        dataset.normalize()
    model.tensorise()

    train_set, val_set = dataset.to_data(batch_size=model.batch_size, shuffle=True, test_size=model.test_size)
    return train_set, val_set


def generate_data(memory: PredictMemory, func: Func, oracle: Optional[Union[Model, HostaDataset]], verbose: bool) -> HostaDataset:
    """
    Generate data for training.
    """
    data = LLMSyntheticDataGenerator.generate_synthetic_data(
        func=func,
        request_amounts=1,  # TODO: make it a parameter
        examples_in_req=5,  # TODO: make it a parameter
        model=oracle if oracle is not None else DefaultModel().get_default_model()
        # verbose=verbose #TODO: ajouter le verbose la !
    )
    return HostaDataset.from_list(data, verbose)


