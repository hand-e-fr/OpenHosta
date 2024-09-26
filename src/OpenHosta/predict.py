import os
import json
import torch

from config import Model, DefaultManager
from builder import Builder
from model import CustomModel
from datapreparator import Datapreparator

CACHE_DIR = "__hostacache__"
os.makedirs(CACHE_DIR, exist_ok=True)

def _exec_predict(
        _function_infos: dict = None,
        _function_obj: object = None,

        encoder = None,
        decoder = None,
        skip_data: list = [],
        out_data: list = [],
        complexity: int = None,
        config: dict = None,
        optimizer: str = None,
        loss: str = None,
        epochs: int = None,
        batch_size: int = None,
        force_train: bool = False,
        norm_max: float = None,
        norm_min: float = None
):
    hidden_dir = os.path.join(CACHE_DIR, f".model_{_function_obj.__name__}_{_function_infos['hash_function']}")
    os.makedirs(hidden_dir, exist_ok=True)

    config_path = os.path.join(hidden_dir, "config.json")
    weight_path = os.path.join(hidden_dir, "model.pth")
    normalisation_path = os.path.join(hidden_dir, "normalisation.json")

    preparator = Datapreparator(norm_max, norm_min, encoder, decoder)
    builder = Builder(hidden_dir)

    if not os.path.exists(config_path) or not os.path.exists(weight_path) or not os.path.exists(normalisation_path) or force_train==True:
        assert _function_infos["ho_example_links"] != [], "No example provided please provide at least one example for the model"

        dataset = preparator.prepare(_function_infos["ho_example_links"], skip_data, out_data)
        dataset_normalize = preparator.normalize_dataset(dataset)
        preparator.save_normalization_params(normalisation_path)

        len_input = len(dataset_normalize[0][0])
        len_output = len(dataset_normalize[0][1])
        #TODO : we will need to add architecture choice after for other type of model
        architecture = builder.build(len_input, len_output, complexity, config, optimizer, loss)
        if batch_size is None:
            batch_size = int(0.05 * len(dataset_normalize)) if 0.05 * len(dataset_normalize) > 1 else 1 # 5% of the dataset or one 
        else:
            batch_size = batch_size
        # print(f"Batch size: {batch_size}")
        train, eval = preparator.split(dataset_normalize, batch_size)

        epochs = int(2*len(dataset_normalize) / batch_size) if epochs is None else epochs
        builder.trains(config, train, eval, epochs=epochs)
    else:
        print("\033[93mModel already trained, skipping training\033[0m")
        preparator.load_normalization_params(normalisation_path)
    
    inference = preparator.prepare_input(_function_infos["function_args"], skip_data)

    inference_normalize = preparator.normalize_inference(inference)
    torch_inference = preparator.convert(inference_normalize)

    prediction = builder.load_inference(config_path, weight_path, torch_inference)
    prediction_denormalize = preparator.denormalize_prediction(prediction)
    result = prediction_denormalize[0]

    return result