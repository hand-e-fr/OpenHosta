from __future__ import annotations

import json
from pydoc import locate

from .emulate import emulate
from ..core.config import DefaultManager
from ..core.hosta import Func
from ..utils.errors import RequestError
from ..utils.meta_prompt import THOUGHT_PROMPT


def guess_type(key: str, *args) -> object:
    l_default = DefaultManager.get_default_model()

    l_user_prompt = (
        "Here's the function behavior:\n"
        + f"{key}\n"
        + "Here's the arguments:\n"
        + f"{args}\n"
    )

    response = l_default.simple_api_call(
        sys_prompt=f"{THOUGHT_PROMPT!r}{THOUGHT_PROMPT.USER_SEP}",
        user_prompt=l_user_prompt,
        temperature=0.5,
    )

    type_json = response["choices"][0]["message"]["content"]
    type_dict = json.loads(type_json)
    type_str = str(type_dict["type"])

    return locate(type_str)


def thinkof(key):

    def inner_func(*args, **kwargs):
        _infos: Func = Func()

        if not hasattr(inner_func, "_return_type"):
            setattr(inner_func, "_return_type", guess_type(key, *args))

        _infos.f_def = key
        _infos.f_call = str([str(arg) for arg in args])
        _infos.f_type = ([type(arg) for arg in args], inner_func._return_type)

        try:
            result = emulate(_infos=_infos)
            setattr(inner_func, "_last_response", result)
        except Exception as e:
            raise RequestError(f"[thinkof] Cannot emulate the function.\n{e}")
        return result

    return inner_func
