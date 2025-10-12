from __future__ import annotations

from typing import Any, Optional

from ..core.config import Model, config

from ..core.meta_prompt import MetaPrompt

def ask(
    user: str,
    system: Optional[str] = "You are a helpful assistant.",
    model: Optional[Model] = None,
    json_output=False,
    **api_args
) -> Any:

    model = config.DefaultModel

    message = []
    if system is not None:
        message.append({"role": "system", "content": system})
    message.append({"role": "user", "content": user})   

    api_args["force_json_output"] = json_output
    
    response_dict = model.api_call(messages=message,
        llm_args=api_args
    )

    response = response_dict["choices"][0]["message"]["content"]

    # No type detection
    answer = response

    return answer
    

async def ask_async(
    user: str,
    system: Optional[str] = "You are a helpful assistant.",
    model: Optional[Model] = None,
    json_output=False,
    **api_args
) -> Any:
    
    model = config.DefaultModel

    message = []
    if system is not None:
        message.append({"role": "system", "content": system})
    message.append({"role": "user", "content": user})   

    api_args["force_json_output"] = json_output

    response_dict = await model.api_call_async(messages=message,
        llm_args=api_args
    )

    response = response_dict["choices"][0]["message"]["content"]
    
    # No type detection
    answer = response

    return answer
    