from __future__ import annotations

from typing import Any, Optional

from ..core.config import Model, DefaultManager
from ..utils.errors import RequestError


def ask(
    *,
    user:str,
    system:Optional[str] = None,
    model:Optional[Model] = None,
    **api_args
)->Any:
    if model is None:
        model = DefaultManager.get_default_model()
    if system is None:
        system = "You are an helpful assistant."
        
    response = model.simple_api_call(
        system,
        user,
        False,
        **api_args
    )
    
    try:
        data = response.json()
        res = data["choices"][0]["message"]["content"]
        setattr(ask, "_last_tokens", data["usage"]["total_tokens"])
        return res
    except Exception as e:
        raise RequestError(f"[ask] Request failed:\n{e}")