from typing import Any, Optional

from ..core.config import config
from ..core.inspection import get_hosta_inspection, Inspection
from ..pipelines import OneTurnConversationPipeline

from ..exec.emulate import emulate

from enum import Enum

class ArgType(Enum):
    str = "str"
    int = "int"
    float = "float"
    bool = "bool"
    list = "list"
    dict = "dict"
    Any = "Any"

def get_most_appropriate_type(request:str) -> ArgType:
    """
    Deduce the most appropriate python type for a given request.
    """
    return emulate()

def guess_type(inspection: Inspection) -> object:
    try:
        detected_type = get_most_appropriate_type(inspection["analyse"]["doc"])
        return eval(detected_type.value, {"Any": Any})
    except Exception as e:
        print(f"Type detection failed for {inspection['analyse']['doc']}: {e}. Returning type 'Any'.")
        return Any

def closure_async(
    query_string,
    *,
    pipeline: Optional[OneTurnConversationPipeline] = config.DefaultPipeline,
    force_return_type: Optional[object] = None,
    force_llm_args: Optional[dict] = {}
    ):

    inner_func_pointer = None

    async def inner_func(*args, **kwargs) -> Any:
                
        # Get everything about the function you are emulating
        inspection = get_hosta_inspection(function_pointer=inner_func_pointer)
        inspection = update_inspection(inspection, query_string, *args, **kwargs)

        # Use return_type if provided, else try to guess it
        if force_return_type is not None:
            inspection["analyse"]["type"] = force_return_type
    
        return_type = inspection["analyse"]["type"]
        if return_type in [None, Any]:
            return_type = guess_type(inspection)
            inspection["analyse"]["type"] = return_type
            
        # Convert the inspection to a prompt
        messages = pipeline.push(inspection)
            
        # This is the api call to the model, nothing more. Easy to debug and test.
        response_dict = await inspection["model"].api_call_async(messages, pipeline.llm_args | force_llm_args)

        # Convert the model response to a python object according to expected types
        response_data = pipeline.pull(inspection, response_dict)
        
        return response_data

    inner_func_pointer = inner_func

    return inner_func

def closure(
    query_string,
    *,
    pipeline: Optional[OneTurnConversationPipeline] = config.DefaultPipeline,
    force_return_type: Optional[object] = None,
    force_llm_args: Optional[dict] = {}
    ):
    
    inner_func_pointer = None
    
    def inner_func(*args, **kwargs) -> Any:
        
        # Get everything about the function you are emulating
        inspection = get_hosta_inspection(function_pointer=inner_func_pointer)
        inspection = update_inspection(inspection, query_string, *args, **kwargs)

        # Use return_type if provided, else try to guess it
        if force_return_type is not None:
            inspection["analyse"]["type"] = force_return_type
    
        return_type = inspection["analyse"]["type"]
        if return_type in [None, Any]:
            return_type = guess_type(inspection)
            inspection["analyse"]["type"] = return_type
        
        # Convert the inspection to a prompt
        messages = pipeline.push(inspection)
            
        # This is the api call to the model, nothing more. Easy to debug and test.
        response_dict = inspection["model"].api_call(messages, pipeline.llm_args | force_llm_args)

        # Convert the model response to a python object according to expected types
        response_data = inspection["pipeline"].pull(inspection, response_dict)

        return response_data
    
    inner_func_pointer = inner_func

    return inner_func

def update_inspection(inspection, query_string, *args, **kwargs):
    
    inspection["analyse"]["doc"] = query_string
    inspection["analyse"]["name"] = "lambda_function"
    inspection["analyse"]["args"]  = [{"name": f"arg_{i}", "type": type(arg), "value": arg} for i, arg in enumerate(args)]
    inspection["analyse"]["args"] += [{"name": name,       "type": type(arg), "value": arg} for name, arg in kwargs.items()]

    return inspection
