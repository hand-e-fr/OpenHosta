from __future__ import annotations

from typing import Any

from ..core.hosta import Hosta, Func
from ..core.config import Model, DefaultManager
from ..utils.prompt import PromptManager

def build_user_prompt(_infos: Func = None, x:Hosta = None):
    filler = lambda pre, value: f"**{pre}**\n{str(value)}\n\n" if value is not None and value != [] else ""
    
    user_prompt = (
        "---\n\n## Function infos\n\n"
        + filler("Here's the function definition:", _infos.f_def)
        + filler("Here's the function's locals variables which you can use as additional information to give your answer:", _infos.f_locals)
        + filler("Here's the type annotation of the function:", _infos.f_type[1])
        + filler("If it isn't a native type, here's a schema describing the type annotation:", _infos.f_schema)
        + "---\n"
    )
    if x:
        user_prompt = (
            user_prompt
            + filler("Here are some examples of expected input and output:", x.example)
            + filler("To solve the request, you have to follow theses intermediate steps. Give only the final result, don't give the result of theses intermediate steps:", x.cot)
            + "---\n"
        )
    print(user_prompt)
    return user_prompt


def emulate(
    model: Model = None,
    temperature: float = None,
    top_p: float = None,
    _infos: Func = None
)->Any:
    x = None
    l_ret:Any = None
    pm = PromptManager()
    meta_prompt:str = pm.get_prompt("emulate")
    
    if _infos is None:
        x = Hosta()
        _infos = x._infos  
    func_prompt:str = build_user_prompt(_infos, x)

    if model is None:
        model = DefaultManager.get_default_model()
    if (temperature is not None and (temperature < 0 or temperature > 1)) or (
        top_p is not None and (top_p < 0 or top_p > 1)
    ):
        raise ValueError("[emulate] Out of range values (0<temperature|top_p<1)")
    
    try:
        response = model.api_call(
            sys_prompt=f"{meta_prompt}\n{func_prompt}\n",
            user_prompt=_infos.f_call,
            temperature=temperature,
            top_p=top_p,
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
