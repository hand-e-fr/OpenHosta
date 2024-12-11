from __future__ import annotations

from typing import Any, Optional, Callable

from ..core.config import Model, DefaultManager
from ..core.hosta import Hosta, Func
from ..utils.meta_prompt import EMULATE_PROMPT


def _build_user_prompt(
        _infos: Func = None,
        x: Hosta = None,
        use_locals_as_ctx: Optional[bool] = False,
        use_self_as_ctx: Optional[bool] = False,
):
    """
    Builds a formatted prompt string for the language model based on function information and context.

    This internal function constructs a structured prompt by combining various pieces of information
    about the target function, including its definition, type hints, schema, and optional context.

    Args:
        _infos (Func): Function information object containing metadata about the target function.
        x (Hosta): Optional Hosta instance containing additional context like examples and chain-of-thought prompts.
        use_locals_as_ctx (Optional[bool]): If True, includes local variable context in the prompt. Defaults to False.
        use_self_as_ctx (Optional[bool]): If True, includes self attributs context for class methods. Defaults to False.

    Returns:
        str: A formatted prompt string containing all relevant function information and context,
            structured with appropriate separators and headers.
    """
    def filler(
        pre, value): return f"**{pre}**\n{str(value)}\n\n" if value is not None and value != [] else ""

    user_prompt = (
        filler(EMULATE_PROMPT.PRE_DEF, _infos.f_def)
        + filler(EMULATE_PROMPT.PRE_TYPE, _infos.f_type[1])
        + filler(EMULATE_PROMPT.PRE_SCHEMA, _infos.f_schema)
    )
    if use_locals_as_ctx:
        user_prompt = (
            user_prompt + filler(EMULATE_PROMPT.PRE_LOCALS, _infos.f_locals))
    if use_self_as_ctx:
        user_prompt = (
            user_prompt + filler(EMULATE_PROMPT.PRE_SELF, _infos.f_self))

    if x:
        ex_str = ""
        if x.example:
            for ex in x.example:
                ex_args = ", ".join(f"{elem[0]}={str(elem[1])}" for elem in [arg for arg in ex["in_"].items()])
                ex_str += f"input: {x.infos.f_name}({ex_args})\noutput: {{return: {str(ex['out'])}}}\n\n"
        user_prompt = (
            user_prompt
            + filler(EMULATE_PROMPT.PRE_EXAMPLE, ex_str)
            + filler(EMULATE_PROMPT.PRE_COT, x.cot)
        )
    user_prompt = (user_prompt + EMULATE_PROMPT.USER_SEP)
    return user_prompt



def emulate(
        _infos: Optional[Func] = None,
        *,
        model: Optional[Model] = None,
        use_locals_as_ctx: bool = False,
        use_self_as_ctx: bool = False,
        post_callback: Optional[Callable] = None,
        **llm_args
) -> Any:
    """
    Emulates a function's behavior using a language model.

    This function uses a language model to emulate the behavior of a Python function
    based on its signature, docstring, and context.
    
    Args:
        - _infos (Optional[Func]): Function information object containing metadata about the target function. If None, creates a new Hosta instance.
        - model (Optional[Model]): The language model to use for emulation. If None, uses the default model.
        - use_locals_as_ctx (bool): If True, includes local variables as context. Defaults to False.
        - use_self_as_ctx (bool): If True, includes self attributs as context for class methods. Defaults to False.
        - post_callback (Optional[Callable]): Optional callback function to process the model's output.
        - **llm_args: Additional keyword arguments to pass to the language model.
    
    Returns:
        - Any: The emulated function's return value, processed by the model and optionally modified by post_callback.
    """
    x = None

    if _infos is None:
        x = Hosta()
        _infos = getattr(x._update_call(), "_infos")
    func_prompt: str = _build_user_prompt(
        _infos, x, use_locals_as_ctx, use_self_as_ctx)

    if model is None:
        model = DefaultManager.get_default_model()

    if x:
        x.attach(_infos.f_obj, { # type: ignore
            "_last_request": None,
            "_last_response": None
        })

    try:
        if x:
            x.attach(_infos.f_obj, {"_last_request": { # type: ignore
                    'sys_prompt':f"{EMULATE_PROMPT!r}\n{func_prompt}\n",
                    'user_prompt':_infos.f_call
                    }
                }
            )
        response = model.api_call([
                {"role": "system", "content": f"{EMULATE_PROMPT!r}\n{func_prompt}\n"},
                {"role": "user", "content": _infos.f_call}
            ],
            **llm_args
        )
        
        if x:
            x.attach(_infos.f_obj, {"_last_response": response}) # type: ignore
        
        l_ret = model.request_handler(response, _infos)
        if post_callback is not None:
            l_ret = post_callback(l_ret)
    except NameError as e:
        raise NotImplementedError(
            f"[emulate]: {e}\nModel object does not have the required methods.")

    return l_ret
