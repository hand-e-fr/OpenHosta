from __future__ import annotations

from typing import Any, Optional

import time
import asyncio

from ..core.inspection import get_caller_frame, get_hosta_inspection
from ..core.config import config
from ..pipelines import OneTurnConversationPipeline
from ..utils.errors import RateLimitError

def emulate(
        *,
        pipeline: Optional[OneTurnConversationPipeline] = config.DefaultPipeline,
        force_llm_args: Optional[dict] = {},
        ) -> Any:
    """
    Emulates a function's behavior using a language model.

    This function uses a language model to emulate the behavior of a Python function
    based on its signature, docstring, and context.
    
    Args:
        - pipeline (Optional[OneTurnConversationPipeline]): The pipeline used for emulation. If None, uses the default one.
        - force_llm_args: Additional keyword arguments to pass to the language model.
    
    Returns:
        - Any: The emulated function's return value, processed by the model and optionally modified by post_callback.
    """
    # You can retrive this frame using get_last_frame(your_emulated_function) in interactive mode
    frame = get_caller_frame()

    # Get everything about the function you are emulating
    inspection = get_hosta_inspection(frame)
    
    # Convert the inspection to a prompt
    messages = pipeline.push(inspection)

    try:
        # This is the api call to the model, nothing more. Easy to debug and test.
        response_dict = inspection["model"].api_call(messages, pipeline.llm_args | force_llm_args)
    except RateLimitError as e:
        print("[emulate] Rate limit exceeded. We wait for 60s then retry.", e)
        time.sleep(60)
        response_dict = inspection["model"].api_call(messages, pipeline.llm_args | force_llm_args)
        
    # Convert the model response to a python object according to expected types
    response_data = pipeline.pull(inspection, response_dict)
    
    return response_data


async def emulate_async(
        *,
        pipeline: Optional[OneTurnConversationPipeline] = config.DefaultPipeline,
        force_llm_args: Optional[dict] = {},
        ) -> Any:
    """
    Emulates a function's behavior using a language model.

    This function uses a language model to emulate the behavior of a Python function
    based on its signature, docstring, and context.
    
    Args:
        - pipeline (Optional[OneTurnConversationPipeline]): The pipeline used for emulation. If None, uses the default one.
        - force_llm_args: Additional keyword arguments to pass to the language model.
    
    Returns:
        - Any: The emulated function's return value, processed by the model and optionally modified by post_callback.
    """
    # You can retrive this frame using get_last_frame(your_emulated_function) in interactive mode
    frame = get_caller_frame()

    # Get everything about the function you are emulating
    inspection = get_hosta_inspection(frame)
    
    # Convert the inspection to a prompt
    messages = pipeline.push(inspection)
    
    try:
        # This is the api call to the model, nothing more. Easy to debug and test.
        response_dict = await inspection["model"].api_call_async(messages, pipeline.llm_args | force_llm_args)
    except RateLimitError as e:
        print("[emulate] Rate limit exceeded. We wait for 60s then retry.", e)
        await asyncio.sleep(60)
        response_dict = inspection["model"].api_call(messages, pipeline.llm_args | force_llm_args)
        
    # Convert the model response to a python object according to expected types
    response_data = pipeline.pull(inspection, response_dict)
    
    return response_data

