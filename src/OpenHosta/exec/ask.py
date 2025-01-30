from __future__ import annotations

from typing import Any, Optional

from ..core.config import Model, DefaultModelPolicy
from ..core.hosta_inspector import FunctionMetadata
from ..utils.errors import RequestError

def ask(
    user: str,
    system: Optional[str] = None,
    model: Optional[Model] = None,
    json_output=False,
    **api_args
) -> Any:
    
    if model is None:
        model = DefaultModelPolicy.get_model()
        
    if system is None:
        system = "You are an helpful assistant."

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
    