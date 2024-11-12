import os
from typing import Union, Optional, Literal

from .model_schema import ConfigModel
from .predict_memory import PredictMemory, File
from .architecture import ArchitectureType, BaseArchitecture
from .architecture.builtins.classification import Classification
from .dataset.dataset import HostaDataset, SourceType

from ...core.hosta import Hosta, Func
from ...core.config import Model, DefaultModel

# from .architecture.builtins.linear_regression import LinearRegressionBuilder

# from .dataset.sample_type import Sample
# from .encoder.simple_encoder import SimpleEncoder

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
    x: Hosta = Hosta()
    func: Func = getattr(x, "_infos")
    name = model.name if model and model.name else func.f_name #TODO: add hash of args into the name of the func

    memory = PredictMemory.load(base_path=model.path, name=name)
    dataset = HostaDataset.get_sample(func.f_args) # just get a sample type of the input, parsing it into one list of value
    
    # Gestion de l'architecture
    architecture = _load_or_create_architecture(memory, func, model)
    
    # Gestion des poids et de l'entraînement
    if not _load_weights_if_exists(memory, architecture):
        _prepare_and_train_model(
            model=model,
            memory=memory,
            dataset=dataset,
            architecture=architecture,
            func=func,
            oracle=oracle,
            verbose=verbose
        )
    # dataset.
    return architecture.inference()


def _load_or_create_architecture(
    memory: PredictMemory,
    func: Func,
    model: Optional[ConfigModel] = None
) -> Architecture:
    """Load or create a new architecture."""
    if memory.architecture.exist:
        json_architecture = memory.architecture.element
        return Architecture.load_architecure_from_json(json_architecture)

    if model is not None:
        if model.model_type == ArchitectureType.LINEAR_REGRESSION:
            architecture = LinearRegressionBuilder()
        elif model.model_type == ArchitectureType.CLASSIFICATION:
            architecture = Classification()
    architecture.save_architecture_to_json(memory.architecture) # à voir si on save dans model ou just on utilise le path (besoin de modif le type File)
    return architecture

def _load_weights_if_exists(
    memory: PredictMemory,
    architecture: Architecture
) -> bool:
    """load weights if they exist."""
    if memory.weight.exist:
        weight = load_weights(memory.weight.element) # rajouter dans config_model un path absolue à des weights ?
        architecture.init_weight(weight) # et assert si les poids ne correspondent pas à l'archi
        return True
    return False

def _prepare_and_train_model(
    model: ConfigModel,
    memory: PredictMemory,
    dataset: HostaDataset,
    architecture: Architecture,
    func: Func,
    oracle: Optional[Union[Model, HostaDataset]],
    verbose: bool
) -> None:
    """Prépare les données et entraîne le modèle."""
    if memory.data_npy.exist:
        dataset.load_data_npy(memory.data_npy.path)
    else:
        _prepare_dataset(model, memory, dataset, func, oracle, verbose)
    
    dataset.prepare_training() # torch, normalization + dataloader
    architecture.training(dataset.train_set, epochs=10, verbose=verbose)
    if verbose:
        dataset.init_example() # validation su les examples (encode....) + un val_test si généré à ajouter
        architecture.eval(dataset.val_set)
    architecture.save_weights(memory.weight)

def _prepare_dataset(
    model: ConfigModel,
    memory: PredictMemory,
    dataset: HostaDataset,
    func: Func,
    oracle: Optional[Union[Model, HostaDataset]],
    verbose: bool
) -> None:
    """Prépare le dataset pour l'entraînement."""
    if not memory.data.exist:
        data = LLMSyntheticDataGenerator.generate_synthetic_data(
            func=func,
            request_amounts=3,  # TODO: make it a parameter
            examples_in_req=50,  # TODO: make it a parameter
            model=oracle if oracle is not None else DefaultModel().get_default_model(),
            verbose=verbose #TODO: ajouter le verbose la !
        )
        dataset.save(memory.data.path, SourceType.CSV, data) # on save le dataset dans le path du memory qu'on vient de générer 
    else:
        dataset.load_data(memory.data) # on charge le dataset depuis le path du memory ou  -> JSON, CSV, Jsonl

    dataset.prepare_data() # sample le dataset
    dataset.encode() # encode + numpy ? 

def load_weights(weight_element : File = None):
    pass





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

