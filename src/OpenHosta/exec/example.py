from __future__ import annotations

from typing import Any, get_args, get_origin, Literal

from ..core.hosta import Hosta, ExampleType


def example(*args, hosta_out: Any = None, **kwargs):
    x = Hosta()
    if args != ():
        raise ValueError(
            "[example] The arguments in example function must be keyword only arguments, with keywords matching with the name of the calling function's arguments"
        )

    expected_return_type = x._infos.f_type[1]

    if not (
        get_origin(expected_return_type) is Literal or
        isinstance(hosta_out, expected_return_type) or
        (expected_return_type == float and isinstance(hosta_out, int)) or
        hosta_out in get_args(expected_return_type) or
        type(hosta_out) in get_args(expected_return_type)
    ):
        raise ValueError(
            "[example] hosta_out's type doesn't match with the calling function's return type:\n\t{} instead of {}."
            .format(type(hosta_out),
            expected_return_type
        ))

    if len(kwargs) != len(x._infos.f_type[0]):
        print(x._infos.f_type[1])
        raise ValueError(
            "[example] Invalid number of argument. Expected {}, got {}"
            .format(len(x._infos.f_type[0]), len(kwargs))
        )

    for (k1, v1), (k2, v2) in zip(kwargs.items(), x._infos.f_args.items()):
        if k1 != k2:
            raise ValueError(
                "[example] Invalid arguments name: Expected {}, got {}"
                .format(k2, k1)
            )
        if type(v1) != type(v2) and not (
            isinstance(v1, int) and isinstance(v2, float) or
            isinstance(v1, float) and isinstance(v2, int)
        ):
            raise ValueError(
                "[example] Invalid arguments type: Expected {}, got {}"
                .format(type(v2), type(v1))
            )

    x._bdy_add('ex', ExampleType(in_=kwargs, out=hosta_out))
