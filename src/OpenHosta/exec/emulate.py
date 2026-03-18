from __future__ import annotations

from typing import Any, Optional

from ..defaults import config

from ..core.inspection import get_caller_frame, get_hosta_inspection

from ..pipelines import OneTurnConversationPipeline

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
    
    # Delegate the entire execution (including retries) to the pipeline
    response_data = pipeline.execute(inspection, force_llm_args)
    
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
    
    # Delegate the entire execution (including retries) to the pipeline
    response_data = await pipeline.execute_async(inspection, force_llm_args)
    
    return response_data
