import sys

from analytics import request_timer
from prompt import PromptMananger
from config import Model, DefaultManager

_x = PromptMananger()

_emulator_pre_prompt = _x.get_prompt("emulate")

l_default = DefaultManager.get_default_model()

def _exec_emulate(
    _function_doc=None,
    _function_call=None,
    _function_return=None,
    model: Model = None,
    warn: bool = False,
    l_creativity: float = None,
    l_diversity: float = None,
):
    global _emulator_pre_prompt

    if model is None:
        model = DefaultManager.get_default_model()

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

    l_user_prompt = (
        "Here's the function definition:\n"
        + _function_doc
        + "\nAnd this is the function call:\n"
        + _function_call
    )
    
    if not _function_return is None:
        l_user_prompt = (
            l_user_prompt 
            + "\nTo fill the “return” value in the output JSON, build your response as defined in the following JSON schema. Do not change the key \"return\"\n"
            + str(_function_return)
        )

    response = model._api_call(
        sys_prompt=_emulator_pre_prompt,
        user_prompt=l_user_prompt,
        creativity=l_creativity,
        diversity=l_diversity,
    )

    l_ret = ""
    
    if response.status_code == 200:
        l_ret = model._request_handler(response)
    else:
        sys.stderr.write(f"Error {response.status_code}: {response.text}")
        l_ret = None
    return l_ret


def thought(key):
    def inner_func(*args, **kwargs):
        try:
            result = _exec_emulate(_function_doc=key, _function_call=str(args[0]))
        except Exception as e:
            sys.stderr.write(Exception)
            sys.stderr.write("[LMDA_ERROR]")
            result = None
        return result

    return inner_func
