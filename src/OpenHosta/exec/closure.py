from typing import Any, Optional

from ..core.config import DefaultPipeline
from ..core.hosta_inspector import get_caller_frame, get_hosta_inspection

from ..core.meta_prompt import MetaPrompt
from ..pipelines import OneTurnConversationPipeline

def guess_type(query: str, inspection) -> object:
    """
    So far this is not ported from V2
    """
    
    return Any


def closure_async(
    query_string,
    *,
    pipeline: Optional[OneTurnConversationPipeline] = DefaultPipeline,
    force_llm_args: Optional[dict] = {}
    ):

    inner_func_pointer = None

    async def inner_func(*args, **kwargs):
        _pipeline = pipeline
        
        # Get everything about the function you are emulating
        inspection = get_hosta_inspection(function_pointer=inner_func_pointer)
        inspection = update_inspection(inspection, query_string, *args, **kwargs)

        # Convert the inspection to a prompt
        messages = pipeline.push(inspection)
            
        # This is the api call to the model, nothing more. Easy to debug and test.
        response_dict = await _pipeline.model.api_call_async(messages, pipeline.llm_args | force_llm_args)

        # Convert the model response to a python object according to expected types
        response_data = _pipeline.pull(response_dict)
        
        return response_data

    inner_func_pointer = inner_func

    return inner_func

def closure(
    query_string,
    *,
    pipeline: Optional[OneTurnConversationPipeline] = DefaultPipeline,
    force_llm_args: Optional[dict] = {}
    ):
    
    inner_func_pointer = None
    
    def inner_func(*args, **kwargs):

        _pipeline = pipeline
        
        # Get everything about the function you are emulating
        inspection = get_hosta_inspection(function_pointer=inner_func_pointer)
        inspection = update_inspection(inspection, query_string, *args, **kwargs)
        
        # Convert the inspection to a prompt
        messages = pipeline.push(inspection)
            
        # This is the api call to the model, nothing more. Easy to debug and test.
        response_dict = _pipeline.model.api_call(messages, pipeline.llm_args | force_llm_args)

        # Convert the model response to a python object according to expected types
        response_data = _pipeline.pull(response_dict)
        
        return response_data
    
    inner_func_pointer = inner_func

    return inner_func


def update_inspection(inspection, query_string, *args, **kwargs):

    return_type = inspection["analyse"]["type"]
    if return_type is None:
        return_type = guess_type(query_string, *args, **kwargs)
        
    inspection["analyse"]["type"] = return_type
    inspection["analyse"]["doc"] = query_string
    inspection["analyse"]["name"] = "lambda_function"
    inspection["analyse"]["args"]  = [{"name": f"arg_{i}", "type": type(arg), "value": arg} for i, arg in enumerate(args)]
    inspection["analyse"]["args"] += [{"name": name,       "type": type(arg), "value": arg} for name, arg in enumerate(kwargs.values())]

    return inspection
