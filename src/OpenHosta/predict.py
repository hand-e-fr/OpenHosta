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
):
    hidden_dir = os.path.join(CACHE_DIR, f".model_{_function_obj.__name__}_{_function_infos['hash_function']}")
    os.makedirs(hidden_dir, exist_ok=True)

    config_path = os.path.join(hidden_dir, "config.json")
    weight_path = os.path.join(hidden_dir, "model.pth")

    if not os.path.exists(config_path) or not os.path.exists(weight_path):
        assert _function_infos["ho_example"] != [], "No example provided please provide at least one example for the model"

        Preparator = Datapreparator(encoder, decoder)
        dataset = Preparator.prepare(_function_infos["ho_example"], skip_data, out_data)

        len_input = len(dataset[0][0])
        len_output = len(dataset[0][1])

        builder = Builder(hidden_dir)
        architecture = builder.build(len_input, len_output, complexity, config, optimizer, loss)

        train, eval = Preparator.split(dataset)
        builder.train(config, architecture, train, eval, epochs)