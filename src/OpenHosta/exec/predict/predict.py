import os
from typing import Union, Optional, Literal

from .model_schema import ConfigModel
from .predict_memory import PredictMemory, File, PredictFileType
from .architecture import ArchitectureType, BaseArchitecture
from .architecture.builtins.classification import Classification
from .dataset.dataset import HostaDataset, SourceType
from .dataset.oracle import LLMSyntheticDataGenerator
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
    func: Func = getattr(Hosta(), "_infos")

    name = model.name if model and model.name else func.f_name #TODO: add hash of args into the name of the func
    base_path = model.path if model and model.path else os.getcwd()
    memory : PredictMemory = PredictMemory.load(base_path=base_path, name=name)

    dataset : HostaDataset = None
    
    architecture : BaseArchitecture = get_architecture(memory, func, model, verbose)

    if not load_weights(memory, architecture):
        train_model(model, memory, architecture, dataset, oracle, verbose)
    
    if dataset is None:
        inference = HostaDataset.from_input(func.f_args, memory, verbose) # Pour le dictionnaire on envoie memory.dictionnary
    else:
        inference = dataset.prepare_input(func.f_args)
    
    prediction = architecture.inference(inference)

    return prediction


# def _load_or_create_architecture(
#     memory: PredictMemory,
#     func: Func,
#     model: Optional[ConfigModel] = None
# ) -> BaseArchitecture:
#     """Load or create a new architecture."""
#     if memory.architecture.exist:
#         json_architecture = memory.architecture.element
#         return BaseArchitecture.load_architecure_from_json(json_architecture)

#     if model is not None:
#         if model.model_type == ArchitectureType.LINEAR_REGRESSION:
#             # architecture = LinearRegression()
#             architecture = None
#         elif model.model_type == ArchitectureType.CLASSIFICATION:
#             architecture = Classification()
#     architecture.save_architecture_to_json(memory.architecture) # à voir si on save dans model ou just on utilise le path (besoin de modif le type File)
#     return architecture
#                     BECOME 
######################################################
def get_architecture(memory: PredictMemory, func: Func, model: Optional[ConfigModel] = None, verbose: bool = False) -> BaseArchitecture:
    """
    Load or create a new architecture.
    """
    if memory.architecture.exist:
        return BaseArchitecture.from_json(memory.architecture.path, verbose) # on à juste changé de nom
    else:
        return BaseArchitecture.from_hosta(func, model, memory.architecture.path, verbose)



# def load_weights(
#     memory: PredictMemory,
#     architecture: BaseArchitecture
# ) -> bool:
#     """load weights if they exist."""
#     if memory.weight.exist:
#         print(" weight exists")
#         weight = memory.weight.element
#         # weight = load_weights(memory.weight.element) # rajouter dans config_model un path absolue à des weights ?
#         # architecture.init_weight(weight) # et assert si les poids ne correspondent pas à l'archi
#         return True
#     print(" weight doesn't exist")
#     return False
#                     BECOME 
######################################################
def load_weights(memory: PredictMemory, architecture: BaseArchitecture) -> bool:
    """
    Load weights if they exist.
    """
    if memory.weight.exist:
        architecture.load_weights(memory.weight.path)
        return True
    return False 

# def train_model(
#     model: ConfigModel,
#     memory: PredictMemory,
#     dataset: HostaDataset,
#     architecture: BaseArchitecture,
#     func: Func,
#     oracle: Optional[Union[Model, HostaDataset]],
#     verbose: bool
# ) -> None:
#     """Prépare les données et entraîne le modèle."""
#     if memory.data_npy.exist:
#         print("  load data from npy")
#         dataset.load_data_npy(memory.data_npy.path)
#     else:
#         print("  prepare dataset don't have numpy")
#         prepare_dataset(model, memory, dataset, func, oracle, verbose)
#     return
#     dataset.prepare_training() # torch, normalization + dataloader
#     architecture.training(dataset.train_set, epochs=10, verbose=verbose)
#     if verbose:
#         dataset.init_example() # validation su les examples (encode....) + un val_test si généré à ajouter
#         architecture.eval(dataset.val_set)
#     architecture.save_weights(memory.weight)
#                     BECOME 
######################################################
def train_model(model: ConfigModel, memory: PredictMemory, architecture: BaseArchitecture, dataset: HostaDataset, oracle: Optional[Union[Model, HostaDataset]], func: Func, verbose: bool) -> None:
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


# def prepare_dataset(
#     model: ConfigModel,
#     memory: PredictMemory,
#     dataset: HostaDataset,
#     func: Func,
#     oracle: Optional[Union[Model, HostaDataset]],
#     verbose: bool
# ) -> None:
#     """Prépare le dataset pour l'entraînement."""
#     if not memory.data.exist:
#         print("   generate data")
#         data = LLMSyntheticDataGenerator.generate_synthetic_data(
#             func=func,
#             request_amounts=3,  # TODO: make it a parameter
#             examples_in_req=50,  # TODO: make it a parameter
#             model=oracle if oracle is not None else DefaultModel().get_default_model()
#             # verbose=verbose #TODO: ajouter le verbose la !
#         )

#         memory.update(PredictFileType.DATA, data.data, SourceType.CSV)
#         memory.data.element = data.data

#     else:
#         print("   load data already exist")
#         dataset.data = memory.data.element
#     dataset.convert_to_sample(memory.data.element) # on charge le dataset depuis le path du memory ou  -> JSON, CSV, Jsonl
#     print("*" * 60)
#     print(memory.data.element)
#     # print(dataset.data)
#     return
#     dataset.encode() # encode + numpy ? 
#                     BECOME 
######################################################
def prepare_dataset(model: ConfigModel, memory: PredictMemory, dataset: HostaDataset, func: Func, oracle: Optional[Union[Model, HostaDataset]], verbose: bool) -> tuple:
    """
    Prepare the dataset for training.
    """
    if model.dataset_path is not None:
        dataset = HostaDataset.from_files(model.dataset_path, SourceType.CSV) # or JSONL jsp comment faire la détection la
    else :
        dataset = generate_data(memory, dataset, func, oracle, verbose) 
    
    dataset.encode()
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
        request_amounts=3,  # TODO: make it a parameter
        examples_in_req=50,  # TODO: make it a parameter
        model=oracle if oracle is not None else DefaultModel().get_default_model()
        # verbose=verbose #TODO: ajouter le verbose la !
    )
    return HostaDataset.from_list(data, verbose)


