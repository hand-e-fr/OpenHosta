from __future__ import annotations

from typing import Any

from .hosta import Hosta
from .config import Model, DefaultManager
from .prompt import PromptMananger

def build_user_prompt(_infos: dict = None):
    filler = lambda pre, value: f"**{pre}**\n{str(value)}\n\n" if value is not None and value != [] else ""
    
    user_prompt = (
        "---\n\n## Function infos\n\n"
        + filler("Here's the function definition:", _infos.f_def)
        + filler("Here's the function's locals variables which you can use as additional information to give your answer:", _infos.f_locals)
        + "To fill in the \"return\" value in the output JSON, create your response according to the specified JSON Schema. Make sure not to change the key \"return.\"\n\n"
        + filler("JSON Schema to be used for \"return\" structure", _infos.f_type)
        # + filler("Here are some examples of expected input and output:", _infos["ho_example"])
        + "---\n"
    )
    return user_prompt


def emulate(
    model: Model = None,
    l_creativity: float = None,
    l_diversity: float = None,
)->Any:
    l_ret:Any = None
    x = Hosta()
    pm = PromptMananger("src/prompt.json")
    meta_prompt:str = pm.get_prompt("emulate")
    func_prompt:str = build_user_prompt(x._infos)

    if model is None:
        model = DefaultManager.get_default_model()
    if (l_creativity is not None and (l_creativity < 0 or l_creativity > 1)) or (
        l_diversity is not None and (l_diversity < 0 or l_diversity > 1)
    ):
        raise ValueError("[emulate] Out of range values (0<creativity|diversity<1)")
    
    try:
        response = model.api_call(
            sys_prompt=f"{meta_prompt}\n{func_prompt}\n",
            user_prompt=x._infos.f_call,
            creativity=l_creativity,
            diversity=l_diversity,
        ),
        l_ret = model.request_handler(
            response[0],
            x._infos.f_type[1], 
            None
        )
    except NameError as e:
        raise NotImplementedError(f"[emulate]: {e}\nModel object does not have the required methods.")
        
    x._attach(x._obj[0], {
        "_last_request": f"{meta_prompt}\n{func_prompt}\n{x._infos.f_call}",
        "_last_response": response[0].json()
        })

    return l_ret
