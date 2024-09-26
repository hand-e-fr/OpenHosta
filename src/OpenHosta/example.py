import inspect
import pickle
import os
import json

from .cache import Hostacache

CACHE_DIR = "__hostacache__"
os.makedirs(CACHE_DIR, exist_ok=True)


def example(*args, hosta_func=None, hosta_out=None, **kwargs):
    input_type = {}
    output_type = {}
    example_dict = {}

    if hosta_func is None:
        try:
            func_frame = inspect.currentframe().f_back
            func_name = func_frame.f_code.co_name
            func = func_frame.f_globals[func_name]
        except:
            raise ValueError(f"Please provide hosta_func for specifying the function")

    elif callable(hosta_func):
        func = hosta_func
    else:
        raise ValueError(f"Please provide hosta_func for specifying the function")

    try:
        sig = inspect.signature(func)
        for param in sig.parameters.values():
            input_type[param.name] = param.annotation
        output_type["hosta_out"] = sig.return_annotation
    except:
        raise ValueError(f"Function does not have signature")
    if args != ():
        if len(args) != len(input_type):
            raise ValueError(
                f"Too many arguments for function {func.__name__}, please provide {len(input_type)} arguments, use hosta_out for output"
            )

        for i, arg in enumerate(args):
            param_name = list(input_type.keys())[i]

            expected_type = input_type[param_name]
            if not isinstance(arg, expected_type):
                raise ValueError(
                    f"Argument {arg} does NOT match the expected type {expected_type} for parameter {param_name}. For function {func.__name__}"
                )
            example_dict[param_name] = arg

    else:
        if len(kwargs) != len(input_type):
            raise ValueError(
                f"Too many arguments for function {func.__name__}, please provide {len(input_type)} arguments, use hosta_out for output"
            )

        for key, value in kwargs.items():
            expected_type = input_type[key]
            if not isinstance(value, expected_type):
                raise ValueError(
                    f"Argument {value} does NOT match the expected type {expected_type} for parameter {key}. For function {func.__name__}"
                )
            example_dict[key] = value

    if hosta_out is None:
        raise ValueError(f"Please provide hosta_out for output")
    else:
        expected_type = output_type["hosta_out"]
        if not isinstance(hosta_out, expected_type):
            raise ValueError(
                f"Output {hosta_out} does NOT match the expected type {expected_type}. For function {func.__name__}"
            )
        example_dict["hosta_out"] = hosta_out

    cache_id = "ho_example"
    cache = Hostacache(func, cache_id, example_dict)
    cache.create_hosta_cache()


def save_examples(hosta_func=None, hosta_path=None):
    cached_data = {}

    if hosta_func is None:
        try:
            func_frame = inspect.currentframe().f_back
            func_name = func_frame.f_code.co_name
            func = func_frame.f_globals[func_name]
        except:
            raise ValueError(f"Please provide hosta_func for specifying the function")

    elif callable(hosta_func):
        func = hosta_func
    else:
        raise ValueError(f"Please provide hosta_func for specifying the function")

    if hosta_path is None:
        raise ValueError(
            f"Please provide hosta_path for specifying the path to save the cache"
        )
    total_path = f"{hosta_path}" + ".jsonl"

    func_name = func.__name__
    path_name = os.path.join(CACHE_DIR, f"{func_name}.openhc")


    try:
        if os.path.exists(path_name):
            with open(path_name, "rb") as f:
                cached_data = pickle.load(f)
                with open(total_path, "a") as t:
                    for dict in cached_data["ho_example"]:
                        t.write(json.dumps(dict) + "\n")
        else:
            raise ValueError(f"Could not found the cache at {path_name}")
    except Exception as e:
        raise ValueError(f"Could not found the cache at {path_name}") from e


def load_examples(hosta_func=None, hosta_path=None):
    if hosta_func is None:
        try:
            func_frame = inspect.currentframe().f_back
            func_name = func_frame.f_code.co_name
            func = func_frame.f_globals[func_name]
        except:
            raise ValueError(f"Please provide hosta_func for specifying the function")

    elif callable(hosta_func):
        func = hosta_func
    else:
        raise ValueError(f"Please provide hosta_func for specifying the function")

    if hosta_path is None:
        raise ValueError(
            f"Please provide hosta_path for specifying the path to load the cache")
    

    path = str(hosta_path)


    _, file_extension = os.path.splitext(path)
    if file_extension != '.jsonl' and file_extension != '.csv':
        raise ValueError("Unsupported file type. Please provide a JSON or CSV file.")
    
    cache_id = "ho_example_links"
    value = path
    cache = Hostacache(func, cache_id, value)
    cache.create_hosta_cache()

