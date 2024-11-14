import os
from typing import Union, Optional, List, Any

from .dataset.dataset import HostaDataset, SourceType
from .dataset.oracle import LLMSyntheticDataGenerator
from .model import HostaModel
from .model.model_provider import HostaModelProvider
from .predict_config import PredictConfig
from .predict_memory import PredictMemory, File
from .model.neural_network import NeuralNetwork
from ...core.config import Model, DefaultModel
from ...core.hosta import Hosta, Func

def predict(
    config: PredictConfig = PredictConfig(),
    oracle: Optional[Union[Model, HostaDataset]] = None, #TODO: function for creating data (call a subclass of oracle ?)
    verbose: int = 0 
) -> Union[int, float, bool, str]:
    """
    Predicts a result using an existing model or by creating a new one.
    
    Args:
        config: Model configuration
        oracle: Reference model or dataset for data generation
        verbose: Enables detailed logging
    
    Returns:
        Model prediction
    """
    assert config is not None, "Please provide a valid configuration not None"
    assert verbose is not None and 0 <= verbose <= 2, "Please provide a valid verbose level (0, 1 or 2)"

    func: Func = getattr(Hosta(), "_infos")

    name = config.name if config and config.name else func.f_name #TODO: add hash of args into the name of the func
    base_path = config.path if config and config.path else os.getcwd()
    memory: PredictMemory = PredictMemory.load(base_path=base_path, name=name)

    dataset: Optional[HostaDataset] = None
    
    hosta_model: HostaModel = get_hosta_model(memory.architecture, func, config, verbose)
    if verbose == 2:
        print(f"[\033[92mArchitecture\033[0m] loaded, type : {type(hosta_model).__name__}")
        
    if not load_weights(memory, hosta_model, verbose):
        train_model(config, memory, hosta_model, dataset, oracle, func, verbose)
    
    if dataset is None:
        dataset = HostaDataset.from_input(func.f_args, verbose)
    else:
        dataset.prepare_inference(func.f_args)
    torch_prediction = hosta_model.inference(dataset.inference._input)
    prediction = dataset.decode(torch_prediction, func_f_type=func.f_type[1])
    return prediction[0] if len(prediction) == 1 else prediction


def get_hosta_model(architecture_file: File, func: Func, config: Optional[PredictConfig] = None, verbose: int = 0) -> HostaModel:
    """
    Load or create a new model.
    """
    architecture: Optional[NeuralNetwork] = None

    if architecture_file.exist:
        with open(architecture_file.path, "r") as file:
            json = file.read()
        architecture = NeuralNetwork.from_json(json)
        if verbose == 2:
            print(f"[\033[92mArchitecture\033[0m] found at {architecture_file.path}")
            # architecture.summary() # TODO: summary
    else:
        if verbose == 2:
            print(f"[\033[93mArchitecture\033[0m] not found, creating one")
    return HostaModelProvider.from_hosta_func(func, config, architecture, architecture_file.path, verbose)


def load_weights(memory: PredictMemory, hosta_model: HostaModel, verbose :int) -> bool:
    """
    Load weights if they exist.
    """
    if memory.weights.exist:

        if verbose == 2:
            print(f"[\033[92mWeights\033[0m] found at {memory.weights.path}")
        hosta_model.init_weights(memory.weights.path)
        return True

    if verbose == 2:
        print(f"[\033[92mWeights\033[0m] not found generate new ones")
    return False 


def train_model(config: PredictConfig, memory: PredictMemory, model: HostaModel, dataset: HostaDataset, oracle: Optional[Union[Model, HostaDataset]], func: Func, verbose: int) -> None:
    """
    Prepare the data and train the model.
    """
    if memory.data.exist:
        if verbose == 2:
            print(f"[\033[92mData\033[0m] found at {memory.data.path}")
        train_set, val_set = HostaDataset.from_data(memory.data.path, batch_size=1, shuffle=True, train_set_size=0.8, verbose=verbose) # verbose will prcess all the example and add it to val_set
    else:
        if verbose == 2:
            print(f"[\033[93mData\033[0m] not processed, preparing data")
        train_set, val_set = prepare_dataset(config, memory, dataset, func, oracle, verbose)
    
    model.trainer(train_set, epochs=100) #TODO: config.epochs
    
    # if verbose:
    #     model.eval(val_set) # or directly in the training method at the end idk me fuck
    
    model.save_weights(memory.weights.path)


def prepare_dataset(config: PredictConfig, memory: PredictMemory, dataset: HostaDataset, func: Func, oracle: Optional[Union[Model, HostaDataset]], verbose: int) -> tuple:
    """
    Prepare the dataset for training.
    """
    if config.dataset_path is not None:
        if verbose == 2:
            print(f"[\033[92mDataset\033[0m] found at {config.dataset_path}")
        dataset = HostaDataset.from_files(config.dataset_path, SourceType.CSV, verbose) # or JSONL jsp comment faire la détection la
    else :
        if verbose == 2:
            print(f"[\033[93mDataset\033[0m]] not found, generate data")
        dataset = generate_data(memory, func, oracle, verbose)
        dataset.save(os.path.join(memory.predict_dir, "generated_data.csv"), SourceType.CSV)
        if verbose == 2:
            print(f"[\033[92mDataset\033[0m] generated!")
    print(dataset.data)
    print(("*-"*50))
    dataset.encode(max_tokens=10)
    print(dataset.data)
    dataset.tensorify()
    print(dataset.data)
    dataset.save_data(memory.data.path)
    print(dataset.data)
    train_set, val_set = dataset.convert_data(batch_size=config.batch_size, shuffle=True, train_set_size=0.8)
    print(dataset.data)

    if verbose == 2:
        print(f"[\033[92mDataset\033[0m] processed and saved at {memory.data.path}")
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


