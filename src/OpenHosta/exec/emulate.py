from __future__ import annotations

from typing import Any, Optional, Callable

import asyncio

from ..core.config import Model, DefaultModelPolicy
from ..core.hosta_inspector import HostaInspector
from ..utils.meta_prompt import Prompt

def emulate(
        *,
        model: Optional[Model] = None,
        prompt: Optional[Prompt] = None,
        use_locals_as_ctx: bool = False,
        use_self_as_ctx: bool = False,
        post_callback: Optional[Callable] = None,
        **llm_args
        ) -> Any:
    """
    Emulates a function's behavior using a language model.

    This function uses a language model to emulate the behavior of a Python function
    based on its signature, docstring, and context.
    
    Args:
        - model (Optional[Model]): The language model to use for emulation. If None, uses the default model.
        - use_locals_as_ctx (bool): If True, includes local variables as context. Defaults to False.
        - use_self_as_ctx (bool): If True, includes self attributs as context for class methods. Defaults to False.
        - post_callback (Optional[Callable]): Optional callback function to process the model's output.
        - **llm_args: Additional keyword arguments to pass to the language model.
    
    Returns:
        - Any: The emulated function's return value, processed by the model and optionally modified by post_callback.
    """
    inspection = HostaInspector()
    return asyncio.run(_emulate(
        inspection=inspection,
        model=model,
        prompt=prompt,
        use_locals_as_ctx=use_locals_as_ctx,
        use_self_as_ctx=use_self_as_ctx,
        post_callback=post_callback,
        llm_args=llm_args,
        ))


async def emulate_async(
        *,
        model: Optional[Model] = None,
        prompt: Optional[Prompt] = None,
        use_locals_as_ctx: bool = False,
        use_self_as_ctx: bool = False,
        post_callback: Optional[Callable] = None,
        **llm_args
        ) -> Any:
    """
    Emulates a function's behavior using a language model.

    This function uses a language model to emulate the behavior of a Python function
    based on its signature, docstring, and context.
    
    Args:
        - model (Optional[Model]): The language model to use for emulation. If None, uses the default model.
        - use_locals_as_ctx (bool): If True, includes local variables as context. Defaults to False.
        - use_self_as_ctx (bool): If True, includes self attributs as context for class methods. Defaults to False.
        - post_callback (Optional[Callable]): Optional callback function to process the model's output.
        - **llm_args: Additional keyword arguments to pass to the language model.
    
    Returns:
        - Any: The emulated function's return value, processed by the model and optionally modified by post_callback.
    """
    inspection = HostaInspector()
    return await _emulate(
        inspection=inspection,
        model=model,
        prompt=prompt,
        use_locals_as_ctx=use_locals_as_ctx,
        use_self_as_ctx=use_self_as_ctx,
        post_callback=post_callback,
        llm_args=llm_args,
        )

async def _emulate(
        *,
        inspection:HostaInspector,
        model: Optional[Model] = None,
        prompt: Optional[Prompt] = None,
        use_locals_as_ctx: bool = False,
        use_self_as_ctx: bool = False,
        post_callback: Optional[Callable] = None,
        **llm_args
) -> Any:

    prompt_data = gather_data_for_prompt_template(inspection, use_locals_as_ctx, use_self_as_ctx)

    if model is None:
        model = DefaultModelPolicy.get_model()

    if prompt is None:
        prompt = DefaultModelPolicy.get_prompt()

    prompt_rendered = prompt.render(prompt_data)

    logging_object = { 
        "_last_request": {},
        "_last_response": {}
    }

    inspection.set_logging_object(logging_object)

    logging_object["_last_request"]['sys_prompt']=prompt_rendered
    logging_object["_last_request"]['user_prompt']=prompt_data["PRE_FUNCTION_CALL"]
    
    try:
        response_dict = await model.api_call_async([
                {"role": "system", "content": prompt_rendered},
                {"role": "user", "content": prompt_data["PRE_FUNCTION_CALL"]}
            ],
            llm_args=llm_args
        )
        
        logging_object["_last_response"]["response_dict"] = response_dict
        
        l_data = model.response_parser(response_dict, inspection._infos)
        l_data = model.type_returned_data(l_data, inspection._infos)
        
        logging_object["_last_response"]["data"] = l_data

        if post_callback is not None:
            l_data = post_callback(l_data)

    except NameError as e:
        raise NotImplementedError(
            f"[emulate]: {e}\nModel object does not have the required methods.")

    return l_data


def gather_data_for_prompt_template(
        inspection: HostaInspector,
        use_locals_as_ctx: Optional[bool] = False,
        use_self_as_ctx: Optional[bool] = False,
):
    """
    Builds a formatted prompt string for the language model based on function information and context.

    This internal function constructs a structured prompt by combining various pieces of information
    about the target function, including its definition, type hints, schema, and optional context.

    Args:
        inspection (HostaInspector): inspection containing additional context like examples and chain-of-thought prompts.
        use_locals_as_ctx (Optional[bool]): If True, includes local variable context in the prompt. Defaults to False.
        use_self_as_ctx (Optional[bool]): If True, includes self attributs context for class methods. Defaults to False.

    Returns:
        str: A formatted prompt string containing all relevant function information and context,
            structured with appropriate separators and headers.
    """
    
    user_prompt_data = {
        "PRE_DEF":inspection._infos.f_def,
        "PRE_TYPE": inspection._infos.f_type[1],
        "PRE_SCHEMA": inspection._infos.f_schema,
        "PRE_FUNCTION_CALL": inspection._infos.f_call
    }

    if use_locals_as_ctx:
        user_prompt_data["PRE_LOCALS"] = inspection._infos.f_locals

    if use_self_as_ctx:
        user_prompt_data["PRE_SELF"] = inspection._infos.f_self

    user_prompt_data["PRE_EXAMPLE"] = []
    for ex in inspection.example:
        ex_args = ", ".join(f"{elem[0]}={str(elem[1])}" for elem in [arg for arg in ex["in_"].items()])
        ex_str = f"input: {inspection.infos.f_name}({ex_args})\noutput: {{return: {str(ex['out'])}}}\n\n"
        user_prompt_data["PRE_EXAMPLE"].append(ex_str)
        
    user_prompt_data["PRE_COT"] = inspection.cot
        
    return user_prompt_data

