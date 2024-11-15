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
    Annotated,
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
from types import MethodType, NoneType
import inspect
from types import FrameType
from typing import Callable, Tuple, List, Dict, Any, Optional, Type

from ..utils.import_handler import is_pydantic

all = (
    "FuncAnalizer"
)


class FuncAnalizer:
    """
    A class for inspecting the signature, definition, and call information of a function.

    Args:
        func (Callable): The function to inspect.

    Attributes:
        func (Callable): The function to inspect.
        sig (Signature): The signature of the function.
    """

    def __init__(self, func: Union[Callable, MethodType] | None, caller_frame: FrameType | None):
        """
        Initialize the function inspector with the given function.

        Args:
            func (Callable): The function to inspect.
            caller_frame (FrameType): The function's frame in which it is called.
        """
        try:
            self.func = func
            self.sig = inspect.signature(func)
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
        func_name = self.func.__name__
        func_params = ", ".join(
            [
                (
                    f"{param_name}: {param.annotation.__name__}"
                    if param.annotation != inspect.Parameter.empty
                    else param_name
                )
                for param_name, param in self.sig.parameters.items()
            ]
        )
        func_return = (
            f" -> {self.sig.return_annotation.__name__}"
            if self.sig.return_annotation != inspect.Signature.empty
            else ""
        )
        definition = (
            f"```python\ndef {func_name}({func_params}):{func_return}\n"
            f"    \"\"\"\n\t{self.func.__doc__}\n    \"\"\"\n```"
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
        if hasattr(self.func, '__self__'):
            values_self = getattr(self.func.__self__, '__dict__', None)
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
        call_str = f"{self.func.__name__}({args_str})"
        return call_str, bound_arguments

    @property
    def func_type(self) -> Tuple[List[Any], Any]:
        """
        Get the _inputs and _outputs types of the function.

        Returns:
            A tuple containing the _inputs types and _outputs type.
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

        if origin in (List, Sequence, Collection):
            return {
                "type": "array",
                "items": self._get_type_schema(args[0]) if args else {"type": "any"}
            }

        if origin in (Dict, Mapping):
            return {
                "type": "object",
                "additionalProperties": self._get_type_schema(args[1]) if args else {"type": "any"}
            }

        if origin is Final:
            return self._get_type_schema(args[0]) if args else {"type": "any"}

        if origin is Type:
            return {"type": "object", "format": "type"}

        if origin is ClassVar:
            return self._get_type_schema(args[0]) if args else {"type": "any"}

        if origin is Annotated:
            return self._get_type_schema(args[0])

        if origin is Literal:
            return {"enum": list(args)}

        if origin is Tuple:
            print("hello")
            if len(args) == 2 and args[1] is ...:
                return {
                    "type": "array",
                    "items": self._get_type_schema(args[0])
                }
            return {
                "type": "array",
                "prefixItems": [self._get_type_schema(arg) for arg in args],
                "items": False
            }

        if origin in (Set, FrozenSet, AbstractSet):
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

        if isinstance(tp, type) and issubclass(tp, Protocol):
            return {"type": "object", "format": "protocol"}

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
            return {"type": "tuple"}
        if tp is set:
            return {"type": "set"}
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
            The JSON schema of the function's return type.
        """
        return_caller = self.sig.return_annotation if self.sig.return_annotation != inspect.Signature.empty else None

        if return_caller is not None:
            if is_pydantic:
                from .pydantic_usage import get_pydantic_schema

                pyd_sch = get_pydantic_schema(return_caller)
                if pyd_sch is not None:
                    return pyd_sch
            return self._get_type_schema(return_caller)
        else:
            return self._get_type_schema(Any)
