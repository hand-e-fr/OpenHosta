import inspect
import sys
from typing import Callable, Any, Dict
from pydantic import BaseModel, create_model

from enhancer import enhance


class HostaInjector:

    def __init__(self, exec):
        if not callable(exec):
            raise TypeError("Executive function must be a function.")
        self.exec = exec

    def __call__(self, *args, **kwargs):
        infos = {"def": "", "call": "", "return_type": ""}

        func_obj, caller = self._extend_scope()
        infos["def"], func_prot = self._get_functionDef(func_obj)
        infos["call"] = self._get_functionCall(func_obj, caller)
        infos["return_type"] = self._get_functionReturnType(func_obj)

        self._attach_attributs(func_obj, func_prot)
        return self.exec(
            infos["def"], infos["call"], infos["return_type"], *args, **kwargs
        )

    def _extend_scope(self) -> Callable:
        func:Callable
    
        try:
            current = inspect.currentframe()
            caller = current.f_back.f_back
            code = current.f_back.f_back.f_code
            for obj in caller.f_back.f_locals.values():
                if hasattr(obj, "__code__"):
                    if obj.__code__ == code:
                        func = obj
                        
            if func is None or not callable(func):
                raise Exception("Larger scope isn't a callable or scope can't be extended.")
        except Exception as e:
            sys.stderr.write(f"[FRAME_ERROR]: {e}")
            func = None
        return func, caller

    def _get_functionDef(self, func: Callable) -> str:
        sig = inspect.signature(func)

        func_name = func.__name__
        func_params = ", ".join(
            [
                (
                    f"{param_name}: {param.annotation.__name__}"
                    if param.annotation != inspect.Parameter.empty
                    else param_name
                )
                for param_name, param in sig.parameters.items()
            ]
        )
        func_return = (
            f" -> {sig.return_annotation.__name__}"
            if sig.return_annotation != inspect.Signature.empty
            else ""
        )
        definition = f"def {func_name}({func_params}):{func_return}\n    '''\n    {func.__doc__}\n    '''"
        prototype = f"def {func_name}({func_params}):{func_return}"
        return definition, prototype

    def _get_functionCall(self, func: Callable, caller) -> str:
        args, _, _, values = inspect.getargvalues(caller)

        sig = inspect.signature(func)
        bound_args = {}
        bound_args = sig.bind_partial(**values)
        bound_args.apply_defaults()

        args_str = ", ".join(
            f"{name}={value!r}" if name in bound_args.kwargs else f"{value!r}"
            for name, value in bound_args.arguments.items()
        )

        call = f"{func.__name__}({args_str})"
        return call

    def _inspect_returnType(self, func: Callable) -> str:
        sig = inspect.signature(func)

        if sig.return_annotation != inspect.Signature.empty:
            return sig.return_annotation
        else:
            return None

    def _get_functionReturnType(self, func: Callable) -> Dict[str, Any]:
        return_type = self._inspect_returnType(func)
        return_json = None

        if return_type is not None:
            if issubclass(return_type, BaseModel):
                return_json = return_type.model_json_schema()
            else:
                new_model = create_model(
                    "Hosta_return_specified", return_hosta_type=(return_type, ...)
                )
                return_json = new_model.model_json_schema()
        else:
            No_return_specified = create_model(
                "Hosta_return_no_specified", return_hosta_type=(Any, ...)
            )
            return_json = No_return_specified.model_json_schema()

        return return_json

    def _attach_attributs(self, func: Callable, prototype: str):
        func.__suggest__ = enhance
        func._prot = prototype
