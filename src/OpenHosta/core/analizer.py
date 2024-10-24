from __future__ import annotations

from typing import Callable, Tuple, List, Dict, Any
from typing import get_args, get_origin
from pydantic import BaseModel, create_model
import inspect
from types import FrameType

all = (
    "_FuncInspector",
    "FuncAnalizer"
)

class _FuncInspector:
    def __init__(self, func: Callable):
        self.func = func
        self.sig = inspect.signature(func)


    def _get_function_signature(self):
        func_name = self.func.__name__
        func_params = ", ".join(
            [
                (
                    f"{param_name}: {param.annotation.__name__}"
                    if param.annotation != inspect.Parameter.empty and hasattr(param.annotation, '__name__')
                    else param_name
                )
                for param_name, param in self.sig.parameters.items()
            ]
        )
        func_return = (
            f" -> {self.sig.return_annotation.__name__}"
            if self.sig.return_annotation != inspect.Signature.empty and hasattr(self.sig.return_annotation, '__name__')
            else ""
        )
        return func_name, func_params, func_return


    def _get_function_definition(self):
        func_name, func_params, func_return = self._get_function_signature()
        definition = (
            f"```python\ndef {func_name}({func_params}):{func_return}\n"
            f"    \"\"\"\n    {self.func.__doc__}\n    \"\"\"\n```"
        )
        prototype = f"def {func_name}({func_params}):{func_return}"
        return definition, prototype


    def _get_call_info(self, caller_frame):
        _, _, _, values = inspect.getargvalues(caller_frame)

        values_args = {k: v for k, v in values.items() if k in self.sig.parameters}
        values_locals = {k: v for k, v in values.items() if k not in self.sig.parameters}

        values_locals.pop('self', None)

        bound_args = self.sig.bind_partial(**values_args)
        bound_args.apply_defaults()

        return bound_args.arguments, values_locals or None


    def _build_call_string(self, bound_arguments):
        args_str = ", ".join(
            f"{k}={v!r}" for k, v in bound_arguments.items()
        )
        call_str = f"{self.func.__name__}({args_str})"
        return call_str

    def _get_function_type(self):
        input_types = [param.annotation for param in self.sig.parameters.values()]
        output_type = self.sig.return_annotation if self.sig.return_annotation != inspect.Signature.empty else None
        return input_types, output_type
    
    def _get_function_schema(self, func: Callable) -> Dict[str, Any]:
        sig = inspect.signature(func)
        return_caller = sig.return_annotation if sig.return_annotation != inspect.Signature.empty else None
        return_schema = None

        if return_caller is not None:
            if get_origin(return_caller):
                return_caller_origin = get_origin(return_caller)
                return_caller_args = get_args(return_caller)
                combined = return_caller_origin[return_caller_args]
                new_model = create_model("return_schema", annotation=(combined, ...))
                return_schema = new_model.model_json_schema()
            elif issubclass(return_caller, BaseModel):
                return_schema = return_caller.model_json_schema()
            else:
                new_model = create_model("return_schema", annotation=(return_caller, ...))
                return_schema = new_model.model_json_schema()
        else:
            No_return_specified = create_model(
                "return_shema", annotation=(Any, ...)
            )
            return_schema = No_return_specified.model_json_schema()
        return return_schema   


class FuncAnalizer(_FuncInspector):
    def __init__(self, func: Callable, caller_frame: FrameType):
        super().__init__(func)
        self.caller_frame = caller_frame

    @property
    def func_def(self) -> str:
        """
        This method returns the function definition and his prototype as a string
        """
        try:
            return self._get_function_definition()
        except:
            raise AttributeError("[FuncAnalizer] Function definition not found")

    @property
    def func_call(self) -> str:
        """
        This method returns the function call as a string
        """
        try:
            bound_args, _ = self._get_call_info(self.caller_frame)
            return self._build_call_string(bound_args)
        except:
            raise AttributeError("[FuncAnalizer] Function call not found")

    @property
    def func_args(self) -> Dict[str, object]:
        """
        This method returns the function arguments as a dictionary
        """
        try:
            bound_args, _ = self._get_call_info(self.caller_frame)
            return bound_args
        except:
            raise AttributeError("[FuncAnalizer] Function arguments not found")

    @property 
    def func_type(self) -> Tuple[List[type], type]:
        """
        This method returns the function input and output types as a tuple
        """
        try:
            return self._get_function_type()
        except:
            raise AttributeError("[FuncAnalizer] Function types not found")

    @property
    def func_locals(self) -> dict:
        """
        This method returns the function local variables as a dictionary
        """
        try:
            _, values_locals = self._get_call_info(self.caller_frame)
            return values_locals
        except:
            raise AttributeError("[FuncAnalizer] Function local variables not found")
        
    @property
    def func_schema(self) -> dict:
        """
        This method returns the function local variables as a dictionary
        """
        try:
            return self._get_function_schema(self.func)
        except:
            raise AttributeError("[FuncAnalizer] Function schema cannot be created")