from __future__ import annotations

from typing import Any, Optional

from ..core.config import DialogueModel, _DefaultNarrator
from ..utils.errors import RequestError

def ask(
    user: str,
    system: Optional[str] = None,
    model: Optional[DialogueModel] = None,
    json_output=False,
    **api_args
) -> Any:
    
    model = _DefaultNarrator.model       

    response_dict = model.api_call([
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        json_output,
        **api_args
    )

    try:
        response = response_dict["choices"][0]["message"]["content"]
        rational, answer = model.split_cot_answer(response)
    except Exception as e:
        raise RequestError(f"[ask] Request failed:\n{e}")

    return answer
    

async def ask_async(
    user: str,
    system: Optional[str] = "You are an helpful assistant.",
    model: Optional[DialogueModel] = None,
    json_output=False,
    **api_args
) -> Any:
    
    model, system = _DefaultNarrator.outline(model, system)       

    response_dict = await model.api_call_async([
            {"role": "system", "content": system.render()},
            {"role": "user", "content": user}
        ],
        json_output,
        **api_args
    )

    try:
        response = response_dict["choices"][0]["message"]["content"]
        rational, answer = model.split_cot_answer(response)
    except Exception as e:
        raise RequestError(f"[ask] Request failed:\n{e}")

    return answer
    