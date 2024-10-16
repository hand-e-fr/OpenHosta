import sys
import inspect

from ..utils.prompt import PromptMananger
from .config import Model, DefaultManager


_x = PromptMananger()

_emulator_pre_prompt = _x.get_prompt("emulate")

l_default = DefaultManager.get_default_model()


def build_user_prompt(_infos: dict = None):
    filler = lambda pre, value: f"**{pre}**\n{str(value)}\n\n" if value is not None and value != [] else ""
    
    user_prompt = (
        "---\n\n## Function infos\n\n"
        + filler("Here's the function definition:", _infos["function_def"])
        + filler("Here's the function's locals variables which you can use as additional information to give your answer:", _infos["function_locals"])
        + "To fill in the \"return\" value in the output JSON, create your response according to the specified JSON Schema. Make sure not to change the key \"return.\"\n\n"
        + filler("JSON Schema to be used for \"return\" structure", _infos["return_type"])
        + filler("Here are some examples of expected input and output:", _infos["ho_example"])
        + "---\n"
    )
    
    return user_prompt


def _exec_emulate(
    _infos: dict = None,
    _obj: object = None,
    model: Model = None,
    l_creativity: float = None,
    l_diversity: float = None,
):
    global _emulator_pre_prompt

    _function_return_caller = _infos["return_caller"]
    _function_return = _infos["return_type"]
    
    if model is None:
        model = DefaultManager.get_default_model() # doublons

    try:
        if not isinstance(_emulator_pre_prompt, str) or not _emulator_pre_prompt:
            raise ValueError("Invalid prompt.")
        if (l_creativity is not None and (l_creativity < 0 or l_creativity > 1)) or (
            l_diversity is not None and (l_diversity < 0 or l_diversity > 1)
        ):
            raise ValueError("Emulate out of range values (0<creativity|diversity<1)")
    except ValueError as v:
        sys.stderr.write(f"[EMULATE_ERROR]: {v}")
        return None

    function_infos = build_user_prompt(_infos)

    response = model.api_call(
        sys_prompt=f"{_emulator_pre_prompt}\n{function_infos}\n",
        user_prompt=_infos["function_call"],
        creativity=l_creativity,
        diversity=l_diversity,
    )
    
    if _obj is not None and inspect.isfunction(_obj):
        setattr(_obj, "_last_response", response.json())
        
    if response.status_code == 200:
        l_ret = model.request_handler(
            response, _function_return, _function_return_caller
        )

    else:
        sys.stderr.write(f"Error {response.status_code}: {response.text}")
        l_ret = None
        
    if _obj is not None and inspect.isfunction(_obj):
        setattr(
            _obj, 
            "_last_request", 
            f"{_emulator_pre_prompt}\n{function_infos}\n{_infos['function_call']}"
        )

    return l_ret
