from __future__ import annotations

from typing import Any, Optional, Callable

from ..core.config import Model, DefaultManager
from ..core.hosta import Hosta, Func
from ..utils.prompt import PromptManager


def _build_user_prompt(
        _infos: Func = None,
        x: Hosta = None,
        use_locals_as_ctx: Optional[bool] = False,
        use_self_as_ctx: Optional[bool] = False,
):
    filler = lambda pre, value: f"**{pre}**\n{str(value)}\n\n" if value is not None and value != [] else ""

    user_prompt = (
            "---\n\n## Function infos\n\n"
            + filler("Here's the function definition:", _infos.f_def)
            + filler("Here's the type annotation of the function:", _infos.f_type[1])
            + filler("If it isn't a native type, here's a schema describing the type annotation:", _infos.f_schema)
    )
    if use_locals_as_ctx:
        user_prompt = (user_prompt + filler("Here's the function's locals variables which you can use as additional information to give your answer:", _infos.f_locals))
    if use_self_as_ctx:
        user_prompt = (user_prompt + filler("Here's the method's class attributs variables which you can use as additional information to give your answer:", _infos.f_self))
    if x:
        user_prompt = (
                user_prompt
                + filler("Here are some examples of expected input and output:", x.example)
                + filler("To solve the request, you have to follow theses intermediate steps. Give only the final result, don't give the result of theses intermediate steps:", x.cot)
        )
    user_prompt = (user_prompt + "---\n")
    return user_prompt


def emulate(
        *,
        model: Optional[Model] = None,
        use_locals_as_ctx: bool = False,
        use_self_as_ctx: bool = False,
        post_callback: Optional[Callable] = None,
        _infos: Optional[Func] = None,
        **llm_args
) -> Any:
    x = None
    l_ret: Any = None
    pm = PromptManager()
    meta_prompt: str = pm.get_prompt("emulate")

    if _infos is None:
        x = Hosta()
        _infos = x._infos
    func_prompt: str = _build_user_prompt(_infos, x, use_locals_as_ctx, use_self_as_ctx)

    if model is None:
        model = DefaultManager.get_default_model()

    try:
        response = model.simple_api_call(
            sys_prompt=f"{meta_prompt}\n{func_prompt}\n",
            user_prompt=_infos.f_call,
            **llm_args
        ),
        l_ret = model.request_handler(response[0], _infos)
        if post_callback is not None:
            l_ret = post_callback(l_ret)
    except NameError as e:
        raise NotImplementedError(f"[emulate]: {e}\nModel object does not have the required methods.")

    if x:
        x._attach(_infos.f_obj, {
            "_last_request": f"{meta_prompt}\n{func_prompt}\n{_infos.f_call}",
            "_last_response": response[0]
        })

    return l_ret
