from typing import Callable, Dict, Any, get_origin, get_args, List
import inspect
import typing
import collections
from pydantic import BaseModel, create_model

def _inspect_returnType(func: Callable) -> str:
    sig = inspect.signature(func)

    if sig.return_annotation != inspect.Signature.empty:
        return sig.return_annotation
    return None

def _get_typingOrigin(return_type) -> bool:
    origin = get_origin(return_type)
    return origin in {
        list,
        dict,
        tuple,
        set,
        frozenset,
        typing.Union,
        typing.Annotated,
        typing.Optional,
        typing.Literal,
        collections.deque,
        collections.abc.Iterable,
        collections.abc.Sequence,
        collections.abc.Mapping,
    }

def _get_functionReturnType(func: Callable) -> Dict[str, Any]:
    return_caller = _inspect_returnType(func)
    return_type = None

    if return_caller is not None:
        if _get_typingOrigin(return_caller):
            return_caller_origin = get_origin(return_caller)
            return_caller_args = get_args(return_caller)
            combined = return_caller_origin[return_caller_args]
            new_model = create_model(
                "Hosta_return_shema", return_hosta_type_typing=(combined, ...)
            )
            return_type = new_model.model_json_schema()
        elif issubclass(return_caller, BaseModel):
            return_type = return_caller.model_json_schema()
        else:
            new_model = create_model(
                "Hosta_return_shema", return_hosta_type=(return_caller, ...)
            )
            return_type = new_model.model_json_schema()
    else:
        No_return_specified = create_model(
            "Hosta_return_shema", return_hosta_type_any=(Any, ...)
        )
        return_type = No_return_specified.model_json_schema()
        
    return return_type, return_caller



class toto(BaseModel):
    tata:str
    titi:int
        
def mutliply(a:int, b:int)->toto:
    """
    This function multiplies two integers in argument.
    """
    return a*b

sig = _inspect_returnType(mutliply)
print(sig)
rt = _get_functionReturnType(mutliply)
print(rt)
