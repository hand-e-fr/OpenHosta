import inspect
import pickle
import os
import json

from .cache import Hostacache

CACHE_DIR = "__hostacache__"
os.makedirs(CACHE_DIR, exist_ok=True)


import inspect

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
            raise ValueError("Please provide hosta_func for specifying the function")
    elif callable(hosta_func):
        func = hosta_func
    else:
        raise ValueError("Please provide hosta_func for specifying the function")

    try:
        sig = inspect.signature(func)
        for param in sig.parameters.values():
            input_type[param.name] = param.annotation
        output_type["hosta_out"] = sig.return_annotation
    except:
        raise ValueError("Function does not have a signature")

    type_verificator(args, kwargs, input_type, output_type, hosta_out, func, example_dict)

    cache_id = "ho_example"
    cache = Hostacache(func, cache_id, example_dict)
    cache.create_hosta_cache()


def type_verificator(args, kwargs, input_type, output_type, hosta_out, func, example_dict):
    """ 
    Validates the types of both positional and keyword arguments, as well as the return value.
    """
    
    if args:
        if len(args) != len(input_type):
            raise ValueError(
                f"Too many arguments for function {func.__name__}, "
                f"expected {len(input_type)} arguments, use hosta_out for output."
            )

        for i, arg in enumerate(args):
            param_name = list(input_type.keys())[i]
            expected_type = input_type[param_name]
            
            if not isinstance(arg, expected_type):
                raise TypeError(
                    f"Argument {arg} does NOT match the expected type "
                    f"{expected_type} for parameter {param_name} in function {func.__name__}."
                )
            example_dict[param_name] = arg

    else:
        if len(kwargs) != len(input_type):
            raise ValueError(
                f"Mismatch in number of keyword arguments for function '{func.__name__}', "
                f"expected {len(input_type)} arguments, use hosta_out for output."
            )

        for key, value in kwargs.items():
            expected_type = input_type[key]
            
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"Keyword argument {value} does NOT match the expected type "
                    f"{expected_type} for parameter {key} in function {func.__name__}."
                )
            example_dict[key] = value

    if hosta_out is None:
        raise ValueError("Please provide hosta_out for output.")
    else:
        expected_output_type = output_type["hosta_out"]
        if not isinstance(hosta_out, expected_output_type):
            raise TypeError(
                f"Output {hosta_out} does NOT match the expected type "
                f"{expected_output_type} for function {func.__name__}."
            )
        example_dict["hosta_out"] = hosta_out


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
                        t.write(json.dumps(dict) + "\n")
        else:
            raise ValueError(f"Could not found the cache at {path_name}")
    except Exception as e:
        raise ValueError(f"Could not found the cache at {path_name}") from e




# def load_examples(hosta_func=None, hosta_path=None):
#     if hosta_func is None:
#         try:
#             func_frame = inspect.currentframe().f_back
#             func_name = func_frame.f_code.co_name
#             func = func_frame.f_globals[func_name]
#         except:
#             raise ValueError(f"Please provide hosta_func for specifying the function")


#     elif callable(hosta_func):
#         func = hosta_func
#     else:
#         raise ValueError(f"Please provide hosta_func for specifying the function")


#     if hosta_path is None:
#         raise ValueError(
#             f"Please provide hosta_path for specifying the path to load the cache")
    

#     path = str(hosta_path)


#     _, file_extension = os.path.splitext(path)
#     if file_extension != '.jsonl' and file_extension != '.csv':
#         raise ValueError("Unsupported file type. Please provide a JSON or CSV file.")
    
#     cache_id = "ho_example_links"
#     value = path
#     cache = Hostacache(func, cache_id, value)
#     cache.create_hosta_cache()



EXAMPLE_DOC = """
A utility function that performs runtime type validation on a given function's arguments and output.

Parameters:
    *args: 
        Positional arguments to validate against the input types of the provided function (hosta_func).
    **kwargs: 
        Keyword arguments (passed by name) to validate against the input types of the provided function.
    hosta_func (function, optional but recommended): 
        The function whose signature will be used for input/output type validation.
    hosta_out (object): 
        The expected output of hosta_func, to be validated against the return type annotation.

Raises:
    ValueError: 
        If the number of arguments provided does not match the expected number as per the function's signature.
    TypeError: 
        If the type of any argument or output does not match the expected type.
    
Usage Example:

"""