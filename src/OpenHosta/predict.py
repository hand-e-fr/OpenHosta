import os

import pickle
from .cache import Hostacache
from .builder import Builder
from .datapreparator import Datapreparator
from .example import type_verificator
from .emulate import _exec_emulate

from typing import Any
import inspect

CACHE_DIR = "__hostacache__"
os.makedirs(CACHE_DIR, exist_ok=True)

def _exec_predict(
        _function_infos: dict = None,
        _function_obj: object = None,

        encoder = None,
        decoder = None,
        verbose: bool = False,
        prediction: list = [],
        complexity: int = None,
        config: dict = None,
        optimizer: str = None,
        loss: str = None,
        epochs: int = None,
        get_loss: float = 0.0,
        batch_size: int = None,
        force_train: bool = False,
        norm_max: float = None,
        norm_min: float = None,
        continue_training: bool = False,
        normalization: bool = False
):
    # print("Predict", flush=True)
    hidden_dir = os.path.join(CACHE_DIR, f".model_{_function_obj.__name__}_{_function_infos['hash_function']}")
    os.makedirs(hidden_dir, exist_ok=True)

    config_path = os.path.join(hidden_dir, "config.json")
    weight_path = os.path.join(hidden_dir, "model.pth")
    normalisation_path = os.path.join(hidden_dir, "normalisation.json")

    preparator = Datapreparator(norm_max, norm_min, encoder, decoder)
    builder = Builder(hidden_dir)

    if not os.path.exists(config_path) or not os.path.exists(weight_path) or force_train==True:

        train, val = preparator.prepare(_function_infos, prediction)
 
        if normalization:  
            train, val = preparator.normalize_dataset(train,val)
            preparator.save_normalization_params(normalisation_path)

        len_input = len(train[0][0])
        len_output = len(train[0][1])
        #TODO : we will need to add architecture choice after for other type of model
        architecture = builder.build(len_input, len_output, complexity, config, optimizer, loss)
        if batch_size is None:
            batch_size = int(0.05 * len(train)) if 0.05 * len(train) > 1 else 1 # 5% of the dataset or one 
        else:
            batch_size = batch_size
        train, eval = preparator.split(train, val, batch_size)

        epochs = int(2*len(train) / batch_size) if epochs is None else epochs
        builder.trains(config, train, eval, epochs=epochs, verbose=verbose, get_loss=get_loss, continue_training=continue_training)
    else:
        if verbose:
            print("\033[93mModel already trained, skipping training\033[0m")
        if normalization:
            preparator.load_normalization_params(normalisation_path)
    if _function_infos["function_args"] != {}:
        inference = preparator.prepare_input(_function_infos["function_args"])
        if normalization:
            inference = preparator.normalize_inference(inference)
        torch_inference = preparator.convert(inference)

        prediction = builder.load_inference(config_path, weight_path, torch_inference)
        if normalization:
            prediction_denormalize = preparator.denormalize_prediction(prediction)
            result = prediction_denormalize[0]
        else:
            result = prediction.detach().cpu().numpy()[0]
        return result


def continue_train(func_obj, epochs=None, get_loss=None, verbose=False):
    """
    Continue the training of the model
    - Reload a pth and add a dataset or not for the model
    save a new pth after the training decided in the emulate or not or in this function also (diff parameters
    of training and not architecture)
    """
    infos_cache = load_cache(func_obj)
    return _exec_predict(_function_infos=infos_cache, _function_obj=func_obj, force_train=True ,continue_training=True, epochs=epochs, get_loss=get_loss, verbose=verbose)


def get_input_types_from_signature(func_obj):
    """
    Extract input type from function signature
    """
    signature = inspect.signature(func_obj)
    input_type = {}
    for name, param in signature.parameters.items():
        if param.annotation != inspect.Parameter.empty:
            input_type[name] = param.annotation
        else:
            input_type[name] = Any
    return input_type


def emulate_verificator(args, kwargs, input_type, func, example_dict):
    """
    Vérifie les types des arguments positionnels et nommés lors de l'appel à emulate.
    Met à jour example_dict avec les valeurs validées.
    """
    param_names = list(input_type.keys())
    
    total_args_provided = len(args) + len(kwargs)
    total_args_expected = len(param_names)
    
    if total_args_provided != total_args_expected:
        raise ValueError(
            f"Incorrect number of arguments for function '{func.__name__}', "
            f"expected {total_args_expected}, got {total_args_provided}."
        )
    
    for i, arg in enumerate(args):
        param_name = param_names[i]
        expected_type = input_type[param_name]
        
        if not isinstance(arg, expected_type):
            raise TypeError(
                f"Positional argument '{param_name}'={arg} does not match the expected type "
                f"{expected_type} in function '{func.__name__}'."
            )
        example_dict[param_name] = arg
    
    for key, value in kwargs.items():
        if key not in input_type:
            raise ValueError(
                f"Unexpected named argument '{key}' for function '{func.__name__}'."
            )
        expected_type = input_type[key]
        
        if not isinstance(value, expected_type):
            raise TypeError(
                f"Named argument '{key}'={value} does not match the expected type "
                f"{expected_type} in function '{func.__name__}'."
            )
        example_dict[key] = value


def to_emulate(*args, func_obj, model=None, l_creativity=None, l_diversity=None, **kwargs):
    """
    Emulate the function with the given arguments and keyword arguments.
    """
    infos_cache = load_cache(func_obj)
    input_type = get_input_types_from_signature(func_obj)

    example_dict = {}

    emulate_verificator(args=args, kwargs=kwargs, input_type=input_type, func=func_obj, example_dict=example_dict)
    infos_cache["function_args"] = example_dict
    
    return _exec_emulate(_infos=infos_cache, _obj=func_obj, model=model, l_creativity=l_creativity, l_diversity=l_diversity)


def load_cache(func_obj):
    func_name = func_obj.__name__
    path_name = os.path.join(CACHE_DIR, f"{func_name}.openhc")

    if os.path.exists(path_name):
        with open(path_name, "rb") as f:
            cached_data = pickle.load(f)
        return cached_data
    else:
        raise ValueError(f"Cache not found for function '{func_name}'.")


def retrain(func_obj=None, force_train=True, epochs=None, get_loss=None, verbose=False):

    infos_cache = load_cache(func_obj)
    return _exec_predict(_function_infos=infos_cache, _function_obj=func_obj, force_train=force_train, epochs=epochs, get_loss=get_loss, verbose=verbose)


def save():
    """
    Save the model in a specified path and a specified name or not
    """
    print("Save")
    pass


def architecture():
    """
    This function is used to change the architecture
    of the model manually or with the help of a llm
    """
    print("Architecture")
    pass














