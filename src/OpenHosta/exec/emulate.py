from __future__ import annotations

from typing import Any
from wsgiref.validate import header_re

from setuptools.sandbox import pushd
from torch.fx.experimental.unification.unification_tools import assoc

from ..core.hosta import Hosta, Func
from ..core.config import Model, DefaultManager
from ..utils.prompt import PromptManager

def build_user_prompt(_infos: Func = None):
    filler = lambda pre, value: f"**{pre}**\n{str(value)}\n\n" if value is not None and value != [] else ""
    
    user_prompt = (
        "---\n\n## Function infos\n\n"
        + filler("Here's the function definition:", _infos.f_def)
        + filler("Here's the function's locals variables which you can use as additional information to give your answer:", _infos.f_locals)
        + filler("Here's the type annotation of the function:", _infos.f_type[1])
        + filler("If it isn't a native type, here's a schema describing the type annotation:", _infos.f_schema)
        # + filler("Here are some examples of expected input and output:", _infos["ho_example"])
        + "---\n"
    )
    return user_prompt


def emulate(
    model: Model = None,
    l_creativity: float = None,
    l_diversity: float = None,
    _infos: Func = None
)->Any:
    x = None
    l_ret:Any = None
    pm = PromptManager()
    meta_prompt:str = pm.get_prompt("emulate")
    
    if _infos is None:
        x = Hosta()
        _infos = x._infos  
    func_prompt:str = build_user_prompt(_infos)

    if model is None:
        model = DefaultManager.get_default_model()
    if (l_creativity is not None and (l_creativity < 0 or l_creativity > 1)) or (
        l_diversity is not None and (l_diversity < 0 or l_diversity > 1)
    ):
        raise ValueError("[emulate] Out of range values (0<creativity|diversity<1)")
    
    try:
        response = model.api_call(
            sys_prompt=f"{meta_prompt}\n{func_prompt}\n",
            user_prompt=_infos.f_call,
            creativity=l_creativity,
            diversity=l_diversity,
        ),
        l_ret = model.request_handler(response[0], _infos)
    except NameError as e:
        raise NotImplementedError(f"[emulate]: {e}\nModel object does not have the required methods.")
    
    if x: 
        x._attach(_infos.f_obj, {
            "_last_request": f"{meta_prompt}\n{func_prompt}\n{_infos.f_call}",
            "_last_response": response[0].json()
            })

    return l_ret
