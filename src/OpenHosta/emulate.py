import sys
import inspect

from .prompt import PromptMananger
from .config import Model, DefaultManager


_x = PromptMananger()

_emulator_pre_prompt = _x.get_prompt("emulate")

l_default = DefaultManager.get_default_model()


def build_user_prompt(_infos: dict = None):
    function_doc = _infos["function_def"]
    function_call = _infos["function_call"]
    function_return = _infos["return_type"]
    function_example = _infos["ho_example"]
    function_locals = _infos["function_locals"]

    user_prompt = (
        "Here's the function definition:\n"
        + function_doc
        + "\nAnd this is the function call:\n"
        + function_call
    )

    if function_example != []:
        user_prompt = (
            user_prompt
            + "\nHere are some examples of expected input and output:\n"
            + str(function_example)
        )

    if not function_return is None:
        user_prompt = (
            user_prompt
            + '\nTo fill the “return” value in the output JSON, build your response as defined in the following JSON schema. Do not change the key "return"\n'
            + str(function_return)
        )

    if function_locals is not None:
        user_prompt = (
            user_prompt
            + "\nHere's the function's locals variables which you can use as additional information to give your answer:\n"
            + str(function_locals)
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

    l_user_prompt = build_user_prompt(_infos)

    response = model.api_call(
        sys_prompt=_emulator_pre_prompt,
        user_prompt=l_user_prompt,
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
        setattr(_obj, "_last_request", f"{_emulator_pre_prompt}\n{l_user_prompt}")

    return l_ret
