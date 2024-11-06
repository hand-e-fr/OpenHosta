from __future__ import annotations

from typing import Callable, Tuple, List, Dict, Any, Optional, Union, OrderedDict
from types import MethodType
import inspect
from types import FrameType

from ..utils.import_handler import is_pydantic

all = (
    "_FuncInspector",
    "FuncAnalizer"
)

class _FuncInspector:
    """
    A class for inspecting the signature, definition, and call information of a function.

    Args:
        func (Callable): The function to inspect.

    Attributes:
        func (Callable): The function to inspect.
        sig (Signature): The signature of the function.
    """
    def __init__(self, func: Union[Callable, MethodType], caller_frame: FrameType):
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
            raise AttributeError(f"[_FuncInspector.__init__] Invalid arguments:\n{e}")

    def _get_function_definition(self)->str:
        """
        Build the string representing the function's definition.

        Returns:
            The string representing the function's definition.
        """
        source = inspect.getsource(self.func)
        definition = f"```python\n{source}\n```"
        return definition


    def _get_function_locals(self)->Tuple[Optional[Dict[str, Any]], Any]:
        """
        Get the attributs and local variables of the function call.

        Returns:
            A tuple containing the bound arguments, local variables, and local attributs.
        """
        values_locals = {k: v for k, v in self.values.items() if k not in self.sig.parameters}
        values_locals.pop('self', None)

        values_self = None
        if hasattr(self.func, '__self__'):
            values_self = getattr(self.func.__self__, '__dict__', None)
        return values_locals or None, values_self


    def _get_function_call(self)->Tuple[str, OrderedDict[str, Any]]:
        """
        Build a string representing the function call.

        Returns:
            A tuple containing a string representing the function call and the bound arguments.
        """
        values_args = {k: v for k, v in self.values.items() if k in self.sig.parameters}
        
        bound_args = self.sig.bind_partial(**values_args)
        bound_args.apply_defaults()
        
        bound_arguments = bound_args.arguments
        
        args_str = ", ".join(
            f"{k}={v!r}" for k, v in bound_arguments.items()
        )
        call_str = f"{self.func.__name__}({args_str})"
        return call_str, bound_arguments

    def _get_function_type(self)->Tuple[List[Any], Any]:
        """
        Get the input and output types of the function.

        Returns:
            A tuple containing the input types and output type.
        """
        input_types = [param.annotation for param in self.sig.parameters.values()]
        output_type = self.sig.return_annotation if self.sig.return_annotation != inspect.Signature.empty else None
        return input_types, output_type
    
    def _get_function_schema(self) -> Dict[str, Any]:
        """
        Get the JSON schema of the function's return type.

        Returns:
            The JSON schema of the function's return type.
        """
        if is_pydantic:
            from .pydantic_usage import get_function_schema_pydantic
            
            return get_function_schema_pydantic(self)
        else:
            return {"type": "integer"}


class FuncAnalizer(_FuncInspector):
    def __init__(self, func: Union[Callable, MethodType], caller_frame: FrameType):
        super().__init__(func, caller_frame)

    @property
    def func_def(self) -> Optional[str]:
        """
        This method returns the function definition and his prototype as a string
        """
        try:
            return self._get_function_definition()
        except:
            raise AttributeError("[FuncAnalizer] Function definition not found")

    @property
    def func_call(self) -> Tuple[str, OrderedDict[str, Any]]:
        """
        This method returns the function call as a string and the bound arguments
        """
        try:
            return self._get_function_call()
        except:
            raise AttributeError("[FuncAnalizer] Function call not found")

    @property 
    def func_type(self) -> Optional[Tuple[List[Any], Any]]:
        """
        This method returns the function input and output types as a tuple
        """
        try:
            return self._get_function_type()
        except:
            raise AttributeError("[FuncAnalizer] Function types not found")

    @property
    def func_locals(self) -> Tuple[Optional[Dict[str, Any]], Any]:
        """
        This method returns the function local variables and attributs.
        """
        try:
            return self._get_function_locals()
        except:
            raise AttributeError("[FuncAnalizer] Function local variables not found")
        
    @property
    def func_schema(self) -> Optional[Dict[str, Any]]:
        """
        This method returns the return schema of the function.
        """
        try:
            return self._get_function_schema()
        except:
            raise AttributeError("[FuncAnalizer] Function schema cannot be created")