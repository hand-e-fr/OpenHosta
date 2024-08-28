import inspect
import sys
from typing import Callable, Any, Type, Dict

from pydantic import BaseModel

from enhancer import enhance

# Add by léandre
class FunctionReturn(BaseModel):
    return_hosta_type: Any = None


class ExecutiveFunction:

    def __init__(self, exec):
        if not callable(exec):
            raise TypeError("Executive function must be a function.")
        self.exec = exec
    
    def __call__(self, *args, **kwargs):
        infos = {"def": "", "call": "", "return_type": ""}
        
        func_obj, caller = self._extend_scope()
        infos["def"], func_prot = self._get_functionDef(func_obj)
        infos["call"] = self._get_functionCall(func_obj, caller)
        # add by léandre
        infos["return_type"] = self._update_returnType(FunctionReturn, func_obj)
    
        # print("infos return JSON: ", infos["return_type"], flush=True)
        self._attach_attributs(func_obj, func_prot)        
        return self.exec(infos["def"], infos["call"], infos["return_type"],*args, **kwargs)
        
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
    
    # Add by léandre
    def _get_functionReturnType(self, func:Callable)->str:
        sig = inspect.signature(func)

        if sig.return_annotation != inspect.Signature.empty:
            return sig.return_annotation
        else:
            return None
    # Add by léandre
    def _translate_PydanticToJson(self, model: Type[BaseModel]) -> Dict[str, Any]:
        structure = {}
        for field_name, field_info in model.__annotations__.items():
            field_type = field_info.__name__
            structure[field_name] = field_type
        return structure

    # Add by léandre
    def _update_returnType(self, model: Type[BaseModel], func: Callable) -> Type[BaseModel]:
        return_type = self._get_functionReturnType(func)

        if return_type is not None:
            if issubclass(return_type, BaseModel):
                model.__annotations__ = return_type.__annotations__
                # print("model new structure : ", model.__annotations__, flush=True)
            else:
                model.__annotations__["return_hosta_type"] = return_type
                # print("model structure : ", model.__annotations__, flush=True)
        else:
            raise Exception("Return type not found.")
        
        Json_model = self._translate_PydanticToJson(model)

        return Json_model
    


    def _attach_attributs(self, func: Callable, prototype:str):
        func.__suggest__ = enhance
        func._prot = prototype