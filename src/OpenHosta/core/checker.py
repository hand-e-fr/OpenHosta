from __future__ import annotations

from types import NoneType
from typing import get_args, get_origin 
from typing import Type, Any, Dict, Optional, Callable
from pydantic import BaseModel

from .hosta import Func


def convert(typ: Type[Any]) -> Optional[Callable[[Any], Any]]:
    return {
        NoneType: lambda x: None,
        str: lambda x: str(x),
        int: lambda x: int(x),
        float: lambda x: float(x),
        list: lambda x: list(x),
        set: lambda x: set(x),
        frozenset: lambda x: frozenset(x),
        tuple: lambda x: tuple(x),
        bool: lambda x: bool(x),
        dict: lambda x: dict(x),
        complex: lambda x: complex(x),
        bytes: lambda x: bytes(x),
    }.get(typ, lambda x: x)

class HostaChecker:
    
    def __init__(self, func: Func, data:dict):
        self.func = func
        self.data = data
        try:
            self.checked = self.data["return"]
            self.is_passed = True
        except KeyError:
            self.checked = self.data
            self.is_passed = False



    def convert_annotated(self)->Any:
        if getattr(self.func.f_type[1], '__module__', None) == 'typing':
            pass
        return self.checked
        #     origin = get_origin(self.func.f_type[1])
        #     args = get_args(self.func.f_type[1])

        #     if origin != None:
        #         if origin in self.convert:
        #             convert_function = self.convert[origin]
        #             return convert_function(self.convert_to_type(d, args[0]) for d in self.checked)
        #     return self.checked
        # else:
        #     return self.checked
        
    def convert_pydantic(self)->Optional[BaseModel]:
        try:
            if issubclass(self.func.f_type[1], BaseModel):
                return self.func.f_type[1](**self.checked)
            return self.checked
        except:
            return self.checked
        
    def check(self)->Any:
        if self.checked == "None":
            return None
        if self.is_passed:
            self.checked = convert(self.func.f_type[1])(self.checked)
            self.checked = self.convert_annotated()
            self.checked = self.convert_pydantic()
        return self.checked
        