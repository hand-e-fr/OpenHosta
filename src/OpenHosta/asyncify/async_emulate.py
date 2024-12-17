from __future__ import annotations

from typing import Any, Optional, Callable

from ..core.config import Model
from ..core.default import DefaultManager
from ..core.hosta import Hosta, Func
from ..utils.meta_prompt import EMULATE_PROMPT
from ..exec.emulate import _build_user_prompt

async def emulate(
        _infos: Optional[Func] = None,
        *,
        model: Optional[Model] = None,
        use_locals_as_ctx: bool = False,
        use_self_as_ctx: bool = False,
        post_callback: Optional[Callable] = None,
        **llm_args
) -> Any:
    """ Same as emulate but async """
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
        response = await model.api_call_async([
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