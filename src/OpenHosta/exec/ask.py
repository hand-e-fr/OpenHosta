from __future__ import annotations

from typing import Any, Union, Callable, Optional
import json

from ..core.config import Model, DefaultManager
from ..utils.errors import RequestError

def ask(
    *,
    system:str,
    user:str,
    model:Optional[Model] = None,
    **api_args
)->Union[Callable, Any]:
    if model is None:
        model = DefaultManager.get_default_model()
    response = model.api_call(
        system,
        user,
        False,
        **api_args
    )
    data = response.json()
    res = data["choices"][0]["message"]["content"]
    setattr(ask, "_last_tokens", data["usage"]["total_tokens"])
    try:
        return res
    except Exception as e:
        raise RequestError(f"[ask] Request failed:\n{e}")