import os
import shutil

from pathlib import Path
from typing import Union, Optional, Literal, Callable

from .dataset.dataset import HostaDataset, SourceType
from .dataset.oracle import LLMSyntheticDataGenerator
from .model import HostaModel
from .model.model_provider import HostaModelProvider
from .model.neural_network import NeuralNetwork
from .model.neural_network_types import ArchitectureType
from .predict_config import PredictConfig
from .predict_memory import PredictMemory, File
from ...core.config import Model, DefaultModelPolicy
from ...core.hosta_inspector import HostaInspector, FunctionMetadata
from ...core.logger import Logger, ANSIColor

def predict(
    config: PredictConfig = PredictConfig(),
    oracle: Optional[Union[Model, HostaDataset]] = None,
    verbose: Union[Literal[0, 1, 2], bool] = 0
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

    inspection = HostaInspector()
    return _predict(
                inspection,
                config,
                oracle,
                verbose
            )

async def predict_async(
    config: PredictConfig = PredictConfig(),
    oracle: Optional[Union[Model, HostaDataset]] = None,
    verbose: Union[Literal[0, 1, 2], bool] = 0
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

    inspection = HostaInspector()
    return _predict(
                inspection,
                config,
                oracle,
                verbose
            )


def _predict(
    inspection: HostaInspector,
    config: PredictConfig = PredictConfig(),
    oracle: Optional[Union[Model, HostaDataset]] = None,
    verbose: Union[Literal[0, 1, 2], bool] = 0
) -> Union[int, float, bool, str]:

    function_metadata = inspection._infos

    name = config.name if config and config.name else str(function_metadata.f_name)
    base_path = config.path if config and config.path else os.getcwd()
    memory: PredictMemory = PredictMemory.load(base_path=base_path, name=name)

    logger: Logger = Logger(log_file_path=memory.summary.path, verbose=verbose)

    dataset: Optional[HostaDataset] = getattr(function_metadata.f_obj, "_dataset", None)

    hosta_model: HostaModel = get_hosta_model(function_metadata, memory.architecture, logger, config)

    #TODO: is this thread safe?
    if not load_weights(inspection, memory, hosta_model, logger):
        train_model(config, memory, hosta_model, oracle, function_metadata, logger)

    if dataset is None:
        dataset = HostaDataset.from_input(function_metadata.f_args, logger, config.max_tokens, function_metadata, memory.dictionary.path)
        inspection.set_logging_object({"_dataset": dataset})
    else:
        dataset.prepare_inference(function_metadata.f_args, config.max_tokens, function_metadata, memory.dictionary.path)

    if not hasattr(function_metadata.f_obj, "_model"):
        setattr(function_metadata, "_model", hosta_model)

    if config.normalize:
        dataset.normalize_input_inference(memory.normalization)
    torch_prediction = hosta_model.inference(dataset.inference.input)
    if config.normalize:
        torch_prediction = dataset.denormalize_output_inference(torch_prediction, memory.normalization)
    output, prediction = dataset.decode(torch_prediction, func_f_type=function_metadata.f_type)
    logger.log_custom("Prediction", f"{prediction} -> {output}", color=ANSIColor.BLUE_BOLD, level=1)
    return output

def clear_training(function_pointer: Callable, config: PredictConfig = PredictConfig()):
    # Valider et nettoyer le nom
    name = config.name if config and config.name else str(function_pointer.__name__)
    name = os.path.basename(name)  # Extrait uniquement le nom de fichier
    
    # Valider et normaliser le chemin de base
    base_path = config.path if config and config.path else os.getcwd()
    base_path = os.path.abspath(base_path)  # Convertit en chemin absolu
    
    # Construire le chemin final de manière sécurisée
    cache_dir = Path(base_path) / "__hostacache__"
    cache_path = cache_dir / name
    
    # Vérifier que le chemin final est bien un sous-répertoire du chemin de base
    try:
        cache_path = cache_path.resolve()
        base_path = Path(base_path).resolve()
        if not str(cache_path).startswith(str(base_path)):
            raise ValueError("Invalid path: attempted directory traversal")
        
        # Supprimer le répertoire s'il existe
        if cache_path.exists():
            shutil.rmtree(str(cache_path))
            
    except (ValueError, RuntimeError) as e:
        raise ValueError(f"Security error: {str(e)}")
        
def clear_training(function_pointer: Callable, config: PredictConfig = PredictConfig()):
    # Valider et nettoyer le nom
    name = config.name if config and config.name else str(function_pointer.__name__)
    name = os.path.basename(name)  # Extrait uniquement le nom de fichier
    
    # Valider et normaliser le chemin de base
    base_path = config.path if config and config.path else os.getcwd()
    base_path = os.path.abspath(base_path)  # Convertit en chemin absolu
    
    # Construire le chemin final de manière sécurisée
    cache_dir = Path(base_path) / "__hostacache__"
    cache_path = cache_dir / name
    
    # Vérifier que le chemin final est bien un sous-répertoire du chemin de base
    try:
        cache_path = cache_path.resolve()
        base_path = Path(base_path).resolve()
        if not str(cache_path).startswith(str(base_path)):
            raise ValueError("Invalid path: attempted directory traversal")
        
        # Supprimer le répertoire s'il existe
        if cache_path.exists():
            shutil.rmtree(str(cache_path))
            
    except (ValueError, RuntimeError) as e:
        raise ValueError(f"Security error: {str(e)}")

def get_hosta_model(function_metadata: FunctionMetadata,
                    architecture_file: File,
                    logger: Logger,
                    config: Optional[PredictConfig] = None) -> HostaModel:
    """
    Load or create a new model.
    """
    if hasattr(function_metadata.f_obj, "_model"):
        return getattr(function_metadata.f_obj, "_model")

    architecture: Optional[NeuralNetwork] = load_architecure(architecture_file, logger)

    model = HostaModelProvider.from_hosta_func(function_metadata, config, architecture, architecture_file.path, logger)
    return model


def load_architecure(architecture_file: File, logger: Logger) -> Union[NeuralNetwork, None]:
    """
    Load the architecture if it exists.
    """
    if architecture_file.exist:
        with open(architecture_file.path, 'r', encoding='utf-8') as file:
            json = file.read()
        logger.log_custom("Architecture", f"found at {architecture_file.path}", color=ANSIColor.BRIGHT_GREEN, level=2)
        return NeuralNetwork.from_json(json)
    else :
        logger.log_custom("Architecture", "not found", color=ANSIColor.BRIGHT_YELLOW, level=2)
        return None

def load_weights(inspection: HostaInspector, memory: PredictMemory, hosta_model: HostaModel, logger: Logger) -> bool:
    """
    Load weights if they exist.
    """
    # if hasattr(inspection._infos.f_obj, "_weights_loaded"):
    #     return True

    if memory.weights.exist:
        logger.log_custom("Weights", f"found at {memory.weights.path}", color=ANSIColor.BRIGHT_GREEN, level=2)
        hosta_model.init_weights(memory.weights.path)
        inspection.set_logging_object({"_weights_loaded": True})
        return True

    logger.log_custom("Weights", "not found", color=ANSIColor.BRIGHT_YELLOW, level=2)
    return False


def train_model(config: PredictConfig,
                memory: PredictMemory,
                model: HostaModel,
                oracle: Optional[Union[Model, HostaDataset]],
                function_metadata: FunctionMetadata,
                logger: Logger) -> None:
    """
    Prepare the data and train the model.
    """
    if memory.data.exist:
        logger.log_custom("Data", f"found at {memory.data.path}", color=ANSIColor.BRIGHT_GREEN, level=2)
        dataset = HostaDataset.from_data(memory.data.path, logger=logger)
        if config.batch_size is None:
            config.batch_size = max(1, min(16384, int(0.05 * len(dataset.data))))

        train_set, val_set = dataset.to_dataloaders(batch_size=config.batch_size, shuffle=True, train_ratio=0.8)

    else:
        logger.log_custom("Data", "not found", color=ANSIColor.BRIGHT_YELLOW, level=2)
        train_set, val_set = prepare_dataset(config, memory, function_metadata, oracle, model, logger)

    logger.log_custom("Training", f"epochs: {config.epochs}, batch_size: {config.batch_size}, train_set size: {len(train_set)}, val_set size: {len(val_set)}", color=ANSIColor.BRIGHT_YELLOW, level=2)

    if config.epochs is None:
        config.epochs = int(2 * len(train_set.dataset) / config.batch_size if config.batch_size != len(train_set.dataset)\
                                else 2 * len(train_set.dataset))
        assert config.epochs > 0, f"epochs must be greater than 0 now it's {config.epochs}"

    model.trainer(train_set, epochs=config.epochs)

    if logger.verbose >= 1:
        model.validate(val_set)


    model.save_weights(memory.weights.path)


def prepare_dataset(config: PredictConfig,
                    memory: PredictMemory,
                    function_metadata: FunctionMetadata,
                    oracle: Optional[Union[Model, HostaDataset]],
                    model: HostaModel,
                    logger: Logger) -> tuple:
    """
    Prepare the dataset for training.
    """

    if config.dataset_path is None:
        generated_data_path = os.path.join(memory.predict_dir, "generated_data.csv")
        if os.path.exists(generated_data_path) and os.path.getsize(generated_data_path) > 0:
            logger.log_custom("Dataset", "no data.json found, but found generated_data.csv, loading it", color=ANSIColor.BRIGHT_GREEN, level=2)
            config.dataset_path = generated_data_path

    if config.dataset_path is not None:
        logger.log_custom("Dataset", f"found at {config.dataset_path}", color=ANSIColor.BRIGHT_GREEN, level=2)
        dataset = HostaDataset.from_files(path=config.dataset_path, source_type=None, log=logger)
    else :
        logger.log_custom("Dataset", "not found, generate data", color=ANSIColor.BRIGHT_YELLOW, level=2)
        dataset = _generate_data(function_metadata, oracle, config, logger)
        save_path = os.path.join(memory.predict_dir, "generated_data.csv")
        dataset.save(save_path, SourceType.CSV)
        logger.log_custom("Dataset", f"generated and saved at {save_path}", color=ANSIColor.BRIGHT_GREEN, level=2)


    if config.batch_size is None:
        config.batch_size = max(1, min(16384, int(0.05 * len(dataset.data))))

    dataset.encode(max_tokens=config.max_tokens, inference=False, function_metadata=function_metadata, dictionary_path=memory.dictionary.path)
    if config.normalize:
        dataset.normalize_data(memory.normalization)
    dataset.tensorize()
    dataset.save_data(memory.data.path)

    train_set, val_set = dataset.to_dataloaders(batch_size=config.batch_size, shuffle=True, train_ratio=0.8)

    logger.log_custom("Dataset", f"processed and saved at {memory.data.path}", color=ANSIColor.BRIGHT_GREEN, level=2)
    return train_set, val_set


def _generate_data(function_metadata: FunctionMetadata,
                   oracle: Optional[Union[Model, HostaDataset]],
                   config: PredictConfig,
                   logger: Logger) -> HostaDataset:
    """
    Generate data for training.
    """
    request_amounts = int(config.generated_data / 100) if config.generated_data > 100 else 1

    data = LLMSyntheticDataGenerator.generate_synthetic_data(
        function_metadata=function_metadata,
        logger=logger,
        request_amounts=request_amounts,
        examples_in_req=int(config.generated_data / request_amounts),
        model=oracle if oracle is not None else DefaultModelPolicy.get_model()
    )
    return HostaDataset.from_list(data, logger)


