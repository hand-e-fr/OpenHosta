from __future__ import annotations

from typing import Any, Optional

from ..core.hosta_inspector import get_caller_frame, get_hota_inspection
from ..core.config import DefaultPipeline
from ..pipelines import Pipeline

def emulate(
        *,
        pipeline: Optional[Pipeline] = DefaultPipeline,
        ) -> Any:
    """
    Emulates a function's behavior using a language model.

    This function uses a language model to emulate the behavior of a Python function
    based on its signature, docstring, and context.
    
    Args:
        - model (Optional[Model]): The language model to use for emulation. If None, uses the default model.
        - post_callback (Optional[Callable]): Optional callback function to process the model's output.
        - llm_args: Additional keyword arguments to pass to the language model.
    
    Returns:
        - Any: The emulated function's return value, processed by the model and optionally modified by post_callback.
    """
    # You can retrive this frame using get_last_frame(your_emulated_function) in interactive mode
    frame = get_caller_frame()

    # Get everything about the function you are emulating
    inspection = get_hota_inspection(frame)
    
    # Convert the inspection to a prompt
    messages = pipeline.push(inspection)
        
    # This is the api call to the model, nothing more. Easy to debug and test.
    response_dict = pipeline.model.api_call(messages, pipeline.conversation.llm_args)

    # Convert the model response to a python object according to expected types
    response_data = pipeline.pull(response_dict)
    
    return response_data


async def emulate_async(
        *,
        pipeline: Optional[Pipeline] = DefaultPipeline,
        ) -> Any:
    """
    Emulates a function's behavior using a language model.

    This function uses a language model to emulate the behavior of a Python function
    based on its signature, docstring, and context.
    
    Args:
        - model (Optional[Model]): The language model to use for emulation. If None, uses the default model.
        - post_callback (Optional[Callable]): Optional callback function to process the model's output.
        - llm_args: Additional keyword arguments to pass to the language model.
    
    Returns:
        - Any: The emulated function's return value, processed by the model and optionally modified by post_callback.
    """
    # You can retrive this frame using get_last_frame(your_emulated_function) in interactive mode
    frame = get_caller_frame()

    inspection = get_hota_inspection(frame)
    
    conversation = pipeline.outline(inspection)
    
    # This where your prompt is. You could also call `conversation.run(data)`
    messages = [
                {"role":role, "content":  meta_prompt.render(conversation.data)}
                    for role, meta_prompt in conversation.meta_conversation
                ]
    
    response_dict = await conversation.model.api_call_async(messages, conversation.llm_args)

    response_data = conversation.parse(response_dict)
    
    return response_data
