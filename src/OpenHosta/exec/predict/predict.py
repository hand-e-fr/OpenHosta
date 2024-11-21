import os
from typing import Union, Optional, Literal

from .dataset.dataset import HostaDataset, SourceType
from .dataset.oracle import LLMSyntheticDataGenerator
from .model import HostaModel
from .model.model_provider import HostaModelProvider
from .model.neural_network import NeuralNetwork
from .predict_config import PredictConfig
from .predict_memory import PredictMemory, File
from ...core.config import Model, DefaultModel
from ...core.hosta import Hosta, Func
from ...core.logger import Logger, ANSIColor


def predict(
    config: PredictConfig = PredictConfig(),
    oracle: Optional[Union[Model, HostaDataset]] = None,
    verbose: Union[Literal[0, 1, 2], bool] = 2
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

    func: Func = getattr(Hosta(), "_infos")

    name = config.name if config and config.name else str(func.f_name)
    base_path = config.path if config and config.path else os.getcwd()
    memory: PredictMemory = PredictMemory.load(base_path=base_path, name=name)

    logger: Logger = Logger(log_file_path=memory.summary.path, verbose=verbose)

    dataset: Optional[HostaDataset] = getattr(func, "_dataset", None)

    hosta_model: HostaModel = get_hosta_model(memory.architecture, func, logger, config)

    if not load_weights(memory, hosta_model, logger):
        train_model(config, memory, hosta_model, dataset, oracle, func, logger)
    
    if dataset is None:
        dataset = HostaDataset.from_input(func.f_args, logger, config.max_tokens, func, memory.dictionary.path)
        setattr(func, "_dataset", dataset)
    else:
        dataset.prepare_inference(func.f_args, config.max_tokens, func, memory.dictionary.path)

    torch_prediction = hosta_model.inference(dataset.inference.input)
    output, prediction = dataset.decode(torch_prediction, func_f_type=func.f_type)
    logger.log_custom("Prediction", f"{prediction} -> {output}", color=ANSIColor.BRIGHT_GREEN)
    return output


def get_hosta_model(architecture_file: File, func: Func, logger: Logger, config: Optional[PredictConfig] = None) -> HostaModel:
    """
    Load or create a new model.
    """
    if hasattr(func, "_model"):
        return getattr(func, "_model")

    architecture: Optional[NeuralNetwork] = None

    if architecture_file.exist:
        with open(architecture_file.path, "r") as file:
            json = file.read()
        architecture = NeuralNetwork.from_json(json)
        logger.log_custom("Architecture", f"found at {architecture_file.path}", color=ANSIColor.BRIGHT_GREEN)
    else:
        logger.log_custom("Architecture", "not found", color=ANSIColor.BRIGHT_YELLOW)
    result = HostaModelProvider.from_hosta_func(func, config, architecture, architecture_file.path, logger)
    logger.log_custom("Architecture", f"loaded, type : {type(result).__name__}", color=ANSIColor.BRIGHT_GREEN)
    setattr(func, "_model", result)
    return result


def load_weights(memory: PredictMemory, hosta_model: HostaModel, logger: Logger) -> bool:
    """
    Load weights if they exist.
    """
    if hasattr(hosta_model, "_weights_loaded"):
        return True

    if memory.weights.exist:
        logger.log_custom("Weights", f"found at {memory.weights.path}", color=ANSIColor.BRIGHT_GREEN)
        hosta_model.init_weights(memory.weights.path)
        setattr(hosta_model, "_weights_loaded", True)
        return True

    logger.log_custom("Weights", "not found", color=ANSIColor.BRIGHT_YELLOW)
    return False


def train_model(config: PredictConfig, memory: PredictMemory, model: HostaModel, dataset: HostaDataset, oracle: Optional[Union[Model, HostaDataset]], func: Func, logger: Logger) -> None:
    """
    Prepare the data and train the model.
    """
    if memory.data.exist:
        logger.log_custom("Data", f"found at {memory.data.path}", color=ANSIColor.BRIGHT_GREEN)
        train_set, val_set = HostaDataset.from_data(memory.data.path, batch_size=1, shuffle=True, train_set_size=0.8, logger=logger)
    else:
        logger.log_custom("Data", "not found", color=ANSIColor.BRIGHT_YELLOW)
        train_set, val_set = prepare_dataset(config, memory, func, oracle, logger)

    if config.epochs is None:
        config.epochs = int(2 * len(train_set.dataset) / config.batch_size if config.batch_size != len(train_set.dataset)\
                                else 2 * len(train_set.dataset))
        assert config.epochs > 0, f"epochs must be greater than 0 now it's {config.epochs}"

    model.trainer(train_set, epochs=config.epochs)
    model.save_weights(memory.weights.path)


def prepare_dataset(config: PredictConfig, memory: PredictMemory, func: Func, oracle: Optional[Union[Model, HostaDataset]], logger: Logger) -> tuple:
    """
    Prepare the dataset for training.
    """

    if config.dataset_path is None:
        generated_data_path = os.path.join(memory.predict_dir, "generated_data.csv")
        if os.path.exists(generated_data_path) and os.path.getsize(generated_data_path) > 0:
            logger.log_custom("Dataset", "no data.json found, but found generated_data.csv, loading it", color=ANSIColor.BRIGHT_GREEN)
            config.dataset_path = generated_data_path

    if config.dataset_path is not None:
        logger.log_custom("Dataset", f"found at {config.dataset_path}", color=ANSIColor.BRIGHT_GREEN)
        dataset = HostaDataset.from_files(config.dataset_path, SourceType.CSV, logger) # or JSONL jsp comment faire la détection la
    else :
        logger.log_custom("Dataset", "not found, generate data", color=ANSIColor.BRIGHT_YELLOW)
        dataset = _generate_data(func, oracle, config, logger)
        save_path = os.path.join(memory.predict_dir, "generated_data.csv")
        dataset.save(save_path, SourceType.CSV)
        logger.log_custom("Dataset", f"generated and saved at {save_path}", color=ANSIColor.BRIGHT_GREEN)

    dataset.encode(max_tokens=config.max_tokens, inference=False, func=func, dictionary_path=memory.dictionary.path)
    dataset.tensorify()
    dataset.save_data(memory.data.path)

    if config.batch_size is None:
        config.batch_size = int(0.05 * len(dataset.data)) if 0.05 * len(dataset.data) > 1 else len(dataset.data)
    train_set, val_set = dataset.convert_data(batch_size=config.batch_size, shuffle=True, train_set_size=0.8)

    logger.log_custom("Dataset", f"processed and saved at {memory.data.path}", color=ANSIColor.BRIGHT_GREEN)
    return train_set, val_set


def _generate_data(func: Func, oracle: Optional[Union[Model, HostaDataset]], config: PredictConfig, logger: Logger) -> HostaDataset:
    """
    Generate data for training.
    """
    request_amounts = int(config.generated_data / 100) if config.generated_data > 100 else 1

    data = LLMSyntheticDataGenerator.generate_synthetic_data(
        func=func,
        logger=logger,
        request_amounts=request_amounts,
        examples_in_req=int(config.generated_data / request_amounts),
        model=oracle if oracle is not None else DefaultModel().get_default_model()
    )
    return HostaDataset.from_list(data, logger)

