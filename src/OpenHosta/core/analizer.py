from __future__ import annotations

from typing import (
    Any,
    Dict,
    get_args,
    get_origin,
    Union,
    List,
    Tuple,
    Mapping,
    Sequence,
    Collection,
    Literal,
    Final,
    Type,
    ClassVar,
    Protocol,
    AnyStr,
    ByteString,
    Set,
    FrozenSet,
    AbstractSet,
    Optional,
    Callable,
    OrderedDict,
    TypeVar
)
from sys import version_info
from types import MethodType
import inspect
from types import FrameType
from typing import Callable, Tuple, List, Dict, Any, Optional, Type, _SpecialGenericAlias

from .pydantic_stub import get_pydantic_schema

if version_info.major == 3 and version_info.minor > 9:
    from types import NoneType
else:
    NoneType = type(None)

all = (
    "FuncAnalizer"
)

def nice_type_name(obj) -> str:
    """
    Get a nice name for the type to insert in function description for LLM.
    """
    if type(obj) is _SpecialGenericAlias:
        t=obj.__repr__()
        t=t.replace("typing.", "")
        return t
    
    if hasattr(obj, "__name__"):
        return obj.__name__

    return str(obj)

class FuncAnalizer:
    """
    A class for inspecting the signature, definition, and call information of a function.

    Args:
        function_pointer (Callable): The function to inspect.

    Attributes:
        function_pointer (Callable): The function to inspect.
        sig (Signature): The signature of the function.
    """

    def __init__(self, function_pointer: Union[Callable, MethodType] | None, caller_frame: FrameType | None):
        """
        Initialize the function inspector with the given function.

        Args:
            function_pointer (Callable): The function to inspect.
            caller_frame (FrameType): The function's frame in which it is called.
        """
        try:
            self.function_pointer = function_pointer
            self.sig = inspect.signature(function_pointer)
            _, _, _, self.values = inspect.getargvalues(caller_frame)
        except Exception as e:
            raise AttributeError(
                f"[_FuncInspector.__init__] Invalid arguments:\n{e}")

    @property
    def func_def(self) -> str:
        """
        Build the string representing the function's definition.

        Returns:
            The string representing the function's definition.
        """
        func_name = getattr(self.function_pointer, "__name__")
        func_params = ", ".join(
            [
                (
                    f"{param_name}: {nice_type_name(param.annotation)}"
                    if param.annotation != inspect.Parameter.empty
                    else param_name
                )
                for param_name, param in self.sig.parameters.items()
            ]
        )
        
        if self.sig.return_annotation is inspect.Signature.empty:
            func_return = ""
        else:
            func_return = " -> " + nice_type_name(self.sig.return_annotation)

        definition = (
            f"```python\ndef {func_name}({func_params}){func_return}:\n"
            f"    \"\"\"{self.function_pointer.__doc__}\"\"\"\n    ...\n```"
        )
        return definition

    @property
    def func_locals(self) -> Tuple[Optional[Dict[str, Any]], Any]:
        """
        Get the attributs and local variables of the function call.

        Returns:
            A tuple containing the bound arguments, local variables, and local attributs.
        """
        values_locals = {k: v for k, v in self.values.items()
                         if k not in self.sig.parameters}
        values_locals.pop('self', None)

        values_self = None
        if hasattr(self.function_pointer, '__self__'):
            values_self = getattr(self.function_pointer.__self__, '__dict__', None)
        return values_locals or None, values_self

    @property
    def func_call(self) -> Tuple[str, OrderedDict[str, Any]]:
        """
        Build a string representing the function call.

        Returns:
            A tuple containing a string representing the function call and the bound arguments.
        """
        values_args = {k: v for k, v in self.values.items()
                       if k in self.sig.parameters}

        bound_args = self.sig.bind_partial(**values_args)
        bound_args.apply_defaults()

        bound_arguments = bound_args.arguments

        args_str = ", ".join(
            f"{k}={v!r}" for k, v in bound_arguments.items()
        )
        call_str = f"{self.function_pointer.__name__}({args_str})"
        return call_str, bound_arguments

    @property
    def func_type(self) -> Tuple[List[Any], Any]:
        """
        Get the inputs and outputs types of the function.

        Returns:
            A tuple containing the inputs types and outputs type.
        """
        input_types = [
            param.annotation for param in self.sig.parameters.values()
        ]
        output_type = self.sig.return_annotation if self.sig.return_annotation != inspect.Signature.empty else None
        return input_types, output_type

    def _get_type_schema(self, tp: Any) -> Dict[str, Any]:
        """
        Generate a JSON schema for a given type.

        Args:
            tp: The type to generate the schema for.

        Returns:
            The JSON schema for the type.
        """
        if tp == Any:
            return {"type": "any"}

        origin = get_origin(tp)
        args = get_args(tp)
        
        res = get_pydantic_schema(tp)
        if res is not None:
            return res

        if origin in (Union, Optional):
            if len(args) == 2 and (NoneType in args or type(None) in args):
                main_type = args[0] if args[1] in (
                    NoneType, type(None)) else args[1]
                return {
                    "anyOf": [
                        self._get_type_schema(main_type),
                        {"type": "null"}
                    ]
                }
            return {"anyOf": [self._get_type_schema(arg) for arg in args]}

        if origin in (list, Sequence.__origin__, Collection.__origin__):
            return {
                "type": "array",
                "items": self._get_type_schema(args[0]) if args else {"type": "any"}
            }

        if origin in (dict, Mapping.__origin__):
            return {
                "type": "object",
                "additionalProperties": self._get_type_schema(args[1]) if args else {"type": "any"}
            }

        if origin is (Final, ClassVar):
            return self._get_type_schema(args[0]) if args else {"type": "any"}

        if origin is Type.__origin__:
            return {"type": "object", "format": "type"}

        if origin is Literal:
            return {"enum": list(args)}

        if origin is tuple:
            if len(args) == 2 and args[1] is ...:
                return {
                    "type": "tuple",
                    "items": self._get_type_schema(args[0])
                }
            return {
                "type": "tuple",
                "prefixItems": [self._get_type_schema(arg) for arg in args],
                "items": False
            }

        if origin in (Set.__origin__, FrozenSet.__origin__, AbstractSet.__origin__):
            return {
                "type": "array",
                "uniqueItems": True,
                "items": self._get_type_schema(args[0]) if args else {"type": "any"}
            }

        if hasattr(tp, "__annotations__") and isinstance(tp, type) and hasattr(tp, "__total__"):
            properties = {
                key: self._get_type_schema(value)
                for key, value in tp.__annotations__.items()
            }
            required = [key for key in properties.keys()] if getattr(
                tp, "__total__", True) else []
            return {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False
            }

        if isinstance(tp, TypeVar):
            if tp.__constraints__:
                return {
                    "anyOf": [
                        self._get_type_schema(constraint)
                        for constraint in tp.__constraints__
                    ]
                }
            elif tp.__bound__:
                return self._get_type_schema(tp.__bound__)
            else:
                return {"type": "any"}

        if tp is int:
            return {"type": "integer"}
        if tp is float:
            return {"type": "number"}
        if tp is str or tp is AnyStr:
            return {"type": "string"}
        if tp is list:
            return {"type": "list"}
        if tp is dict:
            return {"type": "dict"}
        if tp is tuple:
            return {"type": "list"}
        if tp is set:
            return {"type": "list"}
        if tp is frozenset:
            return {"type": "frozenset"}
        if tp is bool:
            return {"type": "boolean"}
        if tp is NoneType or tp is None:
            return {"type": "null"}
        if tp is bytes or tp is bytearray or tp is ByteString:
            return {"type": "string", "format": "binary"}
        raise ValueError(f"{tp} type is not supported please check here to see the supported types : https://github.com/hand-e-fr/OpenHosta/blob/dev/docs/doc.md#:~:text=bool.%20The-,complex,-type%20is%20not")

    @property
    def func_schema(self) -> Dict[str, Any]:
        """
        Get the JSON schema of the function's return type.

        Returns:
            The JSON schema in a dictionary
        """
        if self.sig.return_annotation == inspect.Signature.empty:
            schema = self._get_type_schema(Any)
        else:
            schema = self._get_type_schema(self.sig.return_annotation)
        
        return schema
