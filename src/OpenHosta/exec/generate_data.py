import inspect
import asyncio

from typing import Callable, Optional, Union, Literal

from .predict.dataset.dataset import HostaDataset
from .predict.dataset.oracle import LLMSyntheticDataGenerator
from ..core.config import Model, DefaultModelPolicy
from ..core.hosta_inspector import FunctionMetadata
from ..core.logger import Logger

def _analyze_function(function_pointer: Callable) -> FunctionMetadata: 
    if not callable(function_pointer):
        raise TypeError("The  provided object is not a function or callable.")

    func_obj = FunctionMetadata()
    func_obj.f_name = function_pointer.__name__
    func_obj.f_doc = function_pointer.__doc__ if function_pointer.__doc__ else ""
    func_obj.f_sig = inspect.signature(function_pointer)

    arg_types = {}
    input_types = []

    for name, param in func_obj.f_sig.parameters.items():
        param_type = param.annotation if param.annotation != inspect.Parameter.empty else None
        arg_types[name] = {
            "type": param_type,
            "default": param.default if param.default != inspect.Parameter.empty else None
        }
        input_types.append(param_type)

    func_obj.f_args = arg_types
    return_type = func_obj.f_sig.return_annotation if func_obj.f_sig.return_annotation != inspect.Signature.empty else None
    func_obj.f_type = (input_types, return_type)
    func_obj.f_mem = None

    return func_obj


def generate_data(
        function_pointer: Callable,
        ammount: int,
        oracle: Optional[Model] = None,
        verbose: Union[Literal[0, 1, 2], bool] = 2
):
    return asyncio.run(generate_data_async(
        function_pointer,
        ammount,
        oracle,
        verbose))

async def generate_data_async(
        function_pointer: Callable,
        ammount: int,
        oracle: Optional[Model] = None,
        verbose: Union[Literal[0, 1, 2], bool] = 2
):
    logger: Logger = Logger(verbose=verbose)
    request_amounts = int(ammount / 100) if ammount > 100 else 1

    logger.log_custom("Data Generation", f"Generating {ammount} examples for function {function_pointer.__name__}")
    data = await LLMSyntheticDataGenerator.generate_synthetic_data(
        function_metadata=_analyze_function(function_pointer),
        logger=logger,
        request_amounts=request_amounts,
        examples_in_req=int(ammount / request_amounts),
        model=oracle if oracle is not None else DefaultModelPolicy.get_model()
    )
    return HostaDataset.from_list(data, logger)
