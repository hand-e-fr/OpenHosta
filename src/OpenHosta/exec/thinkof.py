from __future__ import annotations

import json
from pydoc import locate

from ..core.config import DefaultManager
from ..utils.prompt import PromptManager
from .emulate import emulate
from ..core.hosta import Func
from ..utils.errors import RequestError

def guess_type(key:str, *args)->object:
    meta_prompt = PromptManager().get_prompt("thought")
    l_default = DefaultManager.get_default_model()

    l_user_prompt = (
        "Here's the function behavior:\n"
        + f"{key}\n"
        + "Here's the arguments:\n"
        + f"{args}\n"
    )

    response = l_default.api_call(
        sys_prompt=meta_prompt,
        user_prompt=l_user_prompt,
        creativity=0.5,
    )

    data = response.json()
    type_json = data["choices"][0]["message"]["content"]
    type_dict = json.loads(type_json)
    type_str = str(type_dict["type"])

    return locate(type_str)

def thinkof(key):
    
    def inner_func(*args, **kwargs):
        _infos:Func = Func()
        
        if not hasattr(inner_func, "_return_type"):
            setattr(inner_func, "_return_type", guess_type(key, *args))

        _infos.f_def = key 
        _infos.f_call = str(*args)
        _infos.f_type = ([], inner_func._return_type)

        try:
            result = emulate(_infos=_infos)
        except Exception as e:
            raise RequestError(f"[thinkof] Cannot emulate the function.\n{e}")
        return result

    return inner_func
 
 