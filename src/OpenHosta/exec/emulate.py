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
    filler = lambda pre, value: f"**{pre}**\n{str(value)}\n\n" if value is not None and value != [] else ""

    user_prompt = (
            filler(EMULATE_PROMPT.PRE_DEF, _infos.f_def)
            + filler(EMULATE_PROMPT.PRE_TYPE, _infos.f_type[1])
            + filler(EMULATE_PROMPT.PRE_SCHEMA, _infos.f_schema)
    )
    if use_locals_as_ctx:
        user_prompt = (user_prompt + filler(EMULATE_PROMPT.PRE_LOCALS, _infos.f_locals))
    if use_self_as_ctx:
        user_prompt = (user_prompt + filler(EMULATE_PROMPT.PRE_SELF, _infos.f_self))
    if x:
        user_prompt = (
                user_prompt
                + filler(EMULATE_PROMPT.PRE_EXAMPLE, x.example)
                + filler(EMULATE_PROMPT.PRE_COT, x.cot)
        )
    user_prompt = (user_prompt + EMULATE_PROMPT.USER_SEP)
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

    if _infos is None:
        x = Hosta()
        _infos = x._infos
    func_prompt: str = _build_user_prompt(_infos, x, use_locals_as_ctx, use_self_as_ctx)

    if model is None:
        model = DefaultManager.get_default_model()

    try:
        response = model.simple_api_call(
            sys_prompt=f"{EMULATE_PROMPT!r}\n{func_prompt}\n",
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
            "_last_request": f"{EMULATE_PROMPT!r}\n{func_prompt}\n{_infos.f_call}",
            "_last_response": response[0]
        })

    return l_ret
