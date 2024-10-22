from __future__ import annotations

from typing import Any

from .hosta import Hosta, ExampleType

def example(*args, hosta_out:Any=None, **kwargs):
    x =  Hosta()
    if args != ():
        raise ValueError("[example] The arguments in example function must keyword only arguments, with keywords matching with the name of the calling function's arguments")
    if type(hosta_out) != x._infos.f_type[1]:
        raise ValueError("[example] hosta_out's type doesn't match with the calling function's return type:\n\t{} instead of {}.".format(
            type(hosta_out),
            x._infos.f_type[1]
        ))
    if len(kwargs) != len(x._infos.f_type[0]):
        raise ValueError("[example] Invalid number of argument. Expected {}, got {}".format(len(x._infos.f_type[0]), len(kwargs)))
    for (k1, v1), (k2, v2) in zip(kwargs.items(), x._infos.f_args.items()):
        if k1 != k2:
            raise ValueError("[example] Invalid arguments name: Expected {}, got {}".format(k2, k1))
        if type(v1) != type(v2):
            raise ValueError("[example] Invalid arguments type: Expected {}, got {}".format(type(v2), type(v1)))
    x._bdy_add('ex', ExampleType(in_=kwargs, out=hosta_out))
    # vérifier si un example similaire n'a pas déjà été ajouté 
    
# def type_verificator(args, kwargs, input_type, output_type, hosta_out, func, example_dict)->bool:
#     """ 
#     Validates the types of both positional and keyword arguments, as well as the return value.
#     """
    
#     if args:
#         if len(args) != len(input_type):
#             raise ValueError(
#                 f"Too many arguments for function {func.__name__}, "
#                 f"expected {len(input_type)} arguments, use hosta_out for output."
#             )

#         for i, arg in enumerate(args):
#             param_name = list(input_type.keys())[i]
#             expected_type = input_type[param_name]
            
#             if not isinstance(arg, expected_type):
#                 raise TypeError(
#                     f"Argument {arg} does NOT match the expected type "
#                     f"{expected_type} for parameter {param_name} in function {func.__name__}."
#                 )
#             example_dict[param_name] = arg

#     else:
#         if len(kwargs) != len(input_type):
#             raise ValueError(
#                 f"Mismatch in number of keyword arguments for function '{func.__name__}', "
#                 f"expected {len(input_type)} arguments, use hosta_out for output."
#             )

#         for key, value in kwargs.items():
#             expected_type = input_type[key]
            
#             if not isinstance(value, expected_type):
#                 raise TypeError(
#                     f"Keyword argument {value} does NOT match the expected type "
#                     f"{expected_type} for parameter {key} in function {func.__name__}."
#                 )
#             example_dict[key] = value

#     if hosta_out is None:
#         raise ValueError("Please provide hosta_out for output.")
#     else:
#         expected_output_type = output_type["hosta_out"]
#         if not isinstance(hosta_out, expected_output_type):
#             raise TypeError(
#                 f"Output {hosta_out} does NOT match the expected type "
#                 f"{expected_output_type} for function {func.__name__}."
#             )
#         example_dict["hosta_out"] = hosta_out


# def save_examples(hosta_func=None, hosta_path=None):
#     cached_data = {}

#     if hosta_func is None:
#         try:
#             func, _ = _extend_scope()
#         except:
#             raise ValueError(f"Please provide hosta_func for specifying the function")

#     elif callable(hosta_func):
#         func = hosta_func
#     else:
#         raise ValueError(f"Please provide hosta_func for specifying the function")

#     if hosta_path is None:
#         raise ValueError(
#             f"Please provide hosta_path for specifying the path to save the cache"
#         )
#     total_path = f"{hosta_path}" + ".jsonl"

#     func_name = func.__name__
#     path_name = os.path.join(CACHE_DIR, f"{func_name}.openhc")


#     try:
#         if os.path.exists(path_name):
#             with open(path_name, "rb") as f:
#                 cached_data = pickle.load(f)
#                 with open(total_path, "a") as t:
#                     for dict in cached_data["ho_example"]:
#                         t.write(json.dumps(dict) + "\n")
#                         t.write(json.dumps(dict) + "\n")
#         else:
#             raise ValueError(f"Could not found the cache at {path_name}")
#     except Exception as e:
#         raise ValueError(f"Could not found the cache at {path_name}") from e


# def load_training_example(hosta_path: str, hosta_func: callable) -> dict:
#     """
#     Load the training example from the cache.
#     """
#     func_name = hosta_func.__name__
#     path_name = os.path.join(CACHE_DIR, f"{func_name}.openhc")

#     cached_data = None

#     if os.path.exists(path_name):
#         try:
#             with open(path_name, "rb") as f:
#                 cached_data = pickle.load(f)
#         except (pickle.PickleError, IOError) as e:
#             raise ValueError(f"Error loading cache from {path_name}") from e
#     else:
#         cache = Hostacache(hosta_func, None)
#         cache.create_hosta_cache()
#         with open(path_name, "rb") as f:
#             cached_data = pickle.load(f)

#     _, file_extension = os.path.splitext(hosta_path)
#     if file_extension not in ['.json', '.jsonl', '.csv']:
#         raise ValueError("Unsupported file type. Please provide a JSON or JSONL or CSV file.")

#     try:
#         with open(hosta_path, 'r') as file:
#             if file_extension == '.json':
#                 data = json.load(file)
#                 if isinstance(data, list):
#                     for item in data:
#                         if item not in cached_data['ho_data']:
#                             cached_data['ho_data'].append(item)
#                 else:
#                     if data not in cached_data['ho_data']:
#                         cached_data['ho_data'].append(data)
#             elif file_extension == '.jsonl':
#                 for line in file:
#                     item = json.loads(line)
#                     if item not in cached_data['ho_data']:
#                         cached_data['ho_data'].append(item)
#             elif file_extension == '.csv':
#                 reader = csv.DictReader(file)
#                 for row in reader:
#                     if row not in cached_data['ho_data']:
#                         cached_data['ho_data'].append(row)
#         with open(path_name, "wb") as f:
#             pickle.dump(cached_data, f)
#     except (IOError, json.JSONDecodeError) as e:
#         raise ValueError(f"Error loading data from {hosta_path}") from e
#     return cached_data


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
"""