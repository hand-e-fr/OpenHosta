import inspect
import sys
from typing import Callable

from enhancer import enhance

class ExecutiveFunction:

    def __init__(self, exec):
        if not callable(exec):
            raise TypeError("Executive function must be a function.")
        self.exec = exec
    
    def __call__(self, *args, **kwargs):
        infos = {"def": "", "call": ""}
        
        func_obj, caller = self._extend_scope()
        infos["def"], func_prot = self._get_functionDef(func_obj)
        infos["call"] = self._get_functionCall(func_obj, caller)
    
        self.attach_attributs(func_obj, func_prot)        
        return self.exec(infos["def"], infos["call"], *args, **kwargs)
        
    def _extend_scope(self)->Callable:
        try:
            x = inspect.currentframe()
            caller = x.f_back.f_back
            name = caller.f_code.co_name
            func = caller.f_globals.get(name)
            
            if func is None:
                raise Exception("Scope can't be extend.")
            if not callable(func):
                raise Exception("Larger scope isn't a callable.")
        except Exception as e:
            sys.stderr.write(f"[FRAME_ERROR]: {e}")
            return None
        return func, caller
    
    def _get_functionDef(self, func:Callable)->str:
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
    
    def _get_functionCall(self, func:Callable, caller)->str:
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
    
    def attach_attributs(self, func: Callable, prototype:str):
        func.__suggest__ = enhance
        func._prot = prototype