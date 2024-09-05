import inspect
import pickle

from cache import Hostacache

def example(
    *args,
    hosta_func = None,
    hosta_out = None,
    **kwargs
    ):
    input_dict = {}
    output_dict = {}

    if hosta_func is None:
        try :
            func_frame = inspect.currentframe().f_back
            func_name = func_frame.f_code.co_name
            func = func_frame.f_globals[func_name]
        except:
            raise ValueError(f"Please provide hosta_func for specifying the function")
  
    elif callable(hosta_func):
        func = hosta_func

    cache_id = "ho_example"
    value = [args, hosta_out]
    cache = Hostacache(func, cache_id, value)
    cache()

    try:
        sig = inspect.signature(func)
        for param in sig.parameters.values():
            input_dict[param.name] = param.annotation
        output_dict["return"] = sig.return_annotation
    except:
        raise ValueError(f"Function does not have signature")

    if len(args) > len(input_dict):
        raise ValueError(f"Too many arguments for function {func.__name__}, please provide {len(input_dict)} arguments, use hosta_out for output")

    for i, arg in enumerate(args):
        param_name = list(input_dict.keys())[i]
        expected_type = input_dict[param_name]
        
        if not isinstance(arg, expected_type):
            raise ValueError(f"Argument {arg} does NOT match the expected type {expected_type} for parameter {param_name}. For function {func.__name__}")
        
    if hosta_out is None:
        raise ValueError(f"Please provide hosta_out for output")
    else:
        expected_type = output_dict["return"]
        if not isinstance(hosta_out, expected_type):
            raise ValueError(f"Output {hosta_out} does NOT match the expected type {expected_type}. For function {func.__name__}")

    print(f"Argument are good for {func.__name__}")