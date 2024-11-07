import inspect
from types import NoneType
from typing import Any, Dict, get_args, get_origin, Union, List, Tuple


def _get_type_schema(tp: Any) -> Dict[str, Any]:
    """
    Generate a JSON schema for a given type.

    Args:
        tp: The type to generate the schema for.

    Returns:
        The JSON schema for the type.
    """
    print(tp)
    if tp == Any:
        return {"type": "any"}
    
    origin = get_origin(tp)
    args = get_args(tp)
    
    if origin is Union:
        return {"anyOf": [_get_type_schema(arg) for arg in args]}
    
    if origin is list or origin is List:
        return {
            "type": "array",
            "items": _get_type_schema(args[0]) if args else {"type": "any"}
        }
    
    if origin is dict or origin is Dict:
        return {
            "type": "object",
            "additionalProperties": _get_type_schema(args[1]) if args else {"type": "any"}
        }
    
    if origin is tuple or origin is Tuple:
        return {
            "type": "array",
            "prefixItems": [_get_type_schema(arg) for arg in args],
            "items": False
        }
    
    if tp is int:
        return {"type": "integer"}
    if tp is float:
        return {"type": "float"}
    if tp is str:
        return {"type": "string"}
    if tp is bool:
        return {"type": "boolean"}
    if tp is NoneType:
        return {"type": "null"}
    
    raise ValueError(f"Unsupported type: {tp}")

def _get_function_schema_manual(func) -> Dict[str, Any]:
    """
    Get the JSON schema of the function's return type.

    Returns:
        The JSON schema of the function's return type.
    """
    sig = inspect.signature(func)
    return_caller = sig.return_annotation if sig.return_annotation != inspect.Signature.empty else None
    
    if return_caller is not None:
        return _get_type_schema(return_caller)
    else:
        return _get_type_schema(Any)   
    
def test1()->None:
    return

def test2()->Tuple[List[bool], List[bool]]:
    return

class TMP():
    var:str = ""
    
def test3()->TMP:
    return

print(_get_function_schema_manual(test1))
print()
print(_get_function_schema_manual(test2))
