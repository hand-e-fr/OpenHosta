from __future__ import annotations

from typing import Any

from ..core.hosta import Hosta, ExampleType

def example(*args, hosta_out:Any=None, **kwargs):
    x =  Hosta()
    if args != ():
        raise ValueError("[example] The arguments in example function must keyword only arguments, with keywords matching with the name of the calling function's arguments")
    if type(hosta_out) != x._infos.f_type[1]:
        raise ValueError("[example] hosta_out's type doesn't match with the calling function's return type:\n\t{} instead of {}.".format(
            type(hosta_out),
            x._infos.f_type[1]
        ))
    if len(kwargs) != len(x._infos.f_type[0]):
        print(x._infos.f_type[1])
        raise ValueError("[example] Invalid number of argument. Expected {}, got {}".format(len(x._infos.f_type[0]), len(kwargs)))
    for (k1, v1), (k2, v2) in zip(kwargs.items(), x._infos.f_args.items()):
        if k1 != k2:
            raise ValueError("[example] Invalid arguments name: Expected {}, got {}".format(k2, k1))
        if type(v1) != type(v2):
            raise ValueError("[example] Invalid arguments type: Expected {}, got {}".format(type(v2), type(v1)))
    x._bdy_add('ex', ExampleType(in_=kwargs, out=hosta_out))