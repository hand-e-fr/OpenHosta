import pickle
import os
import hashlib
import inspect
from typing import Callable, Dict, Any, get_origin, get_args
import typing
import collections
from pydantic import BaseModel, create_model
import sys
import copy

from .enhancer import enhance
from .errors import FrameError


CACHE_DIR = "__hostacache__"
os.makedirs(CACHE_DIR, exist_ok=True)


class HostaInjector:
    def __init__(self, exec):
        if not callable(exec):
            raise TypeError("Executive function must be a function.")

        self.exec = exec
        self.infos_cache = {}

    def __call__(self, *args, **kwargs):
        self.infos_cache = {
            "hash_function": "",
            "function_def": "",
            "return_type": "",
            "return_caller": "",
            "function_call": "",
            "function_locals": {},
            "ho_example": [],
            "ho_example_id": 0,
            "ho_cothougt": [],
            "ho_cothougt_id": 0,
        }
        func_obj, caller = self._extend_scope()
        func_name = func_obj.__name__
        path_name = os.path.join(CACHE_DIR, f"{func_name}.openhc")

        if os.path.exists(path_name):
            with open(path_name, "rb") as f:
                cached_data = pickle.load(f)

            function_def, func_prot = self._get_functionDef(func_obj)
            function_hash = self._get_hashFunction(
                function_def,
                cached_data["ho_example_id"],
                cached_data["ho_cothougt_id"],
            )

            if function_hash == cached_data["hash_function"]:
                cached_data["function_call"], cached_data["function_locals"] = (
                    self._get_functionCall(func_obj, caller)
                )
                self._attach_attributs(func_obj, func_prot)
                return self.exec(cached_data, func_obj, *args, **kwargs)

        hosta_args = self._get_argsFunction(func_obj)
        with open(path_name, "wb") as f:
            res = pickle.dump(hosta_args, f)
        # TODO : fix the function locals because he didn't load in the cache
        hosta_args["function_call"], hosta_args["function_locals"] = (
            self._get_functionCall(func_obj, caller)
        )
        return self.exec(hosta_args, func_obj, *args, **kwargs)

    def _get_hashFunction(self, func_def: str, nb_example: int, nb_thought: int) -> str:
        combined = f"{func_def}{nb_example}{nb_thought}"
        return hashlib.md5(combined.encode()).hexdigest()

    def _get_argsFunction(self, func_obj):

        self.infos_cache["function_def"], func_prot = self._get_functionDef(func_obj)
        self.infos_cache["return_type"], self.infos_cache["return_caller"] = (
            self._get_functionReturnType(func_obj)
        )
        self.infos_cache["hash_function"] = self._get_hashFunction(
            self.infos_cache["function_def"],
            self.infos_cache["ho_example_id"],
            self.infos_cache["ho_cothougt_id"],
        )
        self._attach_attributs(func_obj, func_prot)
        return self.infos_cache

    def _extend_scope(self) -> Callable:
        func: Callable = None
        current = None
        step = None
        caller = None

        current = inspect.currentframe()
        if current is None:
            raise FrameError("Current frame is None")
        step = current.f_back
        if step is None:
            raise FrameError("Caller[lvl1] frame is None")
        caller = step.f_back
        if caller is None:
            raise FrameError("Caller[lvl2] frame is None")

        caller_name = caller.f_code.co_name
        caller_code = caller.f_code
        l_caller = caller
        
        if "self" in caller.f_locals:
            obj = caller.f_locals["self"]
            func = getattr(obj, caller_name, None)
            if func:
                func = inspect.unwrap(func)
        else:
            while func is None and l_caller.f_back is not None:
                for obj in l_caller.f_back.f_locals.values():
                    found = False
                    try:
                        if hasattr(obj, "__code__"):
                            found = True
                    except:
                        continue       
                    if found and obj.__code__ == caller_code:
                        func = obj
                        break
                if func is None:
                    l_caller = l_caller.f_back
            if func is None:
                func = caller.f_globals.get(caller_name)
                if func:
                    func = inspect.unwrap(func)
        
        if func is None or not callable(func):
            raise FrameError("The emulated function cannot be found.")

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
        locals = None
        _, _, _, values = inspect.getargvalues(caller)

        sig = inspect.signature(func)

        values_args = copy.deepcopy(values)
        values_locals = copy.deepcopy(values)
        for values_name in values.keys():
            if values_name not in sig.parameters.keys():
                values_args.pop(values_name)
            else:
                values_locals.pop(values_name)

        if "self" in values_locals.keys():
            values_locals.pop("self")

        if values_locals != {}:
            locals = copy.deepcopy(values_locals)

        bound_args = sig.bind_partial(**values_args)
        bound_args.apply_defaults()

        args_str = ", ".join(
            f"{name}={value!r}" if name in bound_args.kwargs else f"{value!r}"
            for name, value in bound_args.arguments.items()
        )

        call = f"{func.__name__}({args_str})"
        return call, locals

    def _inspect_returnType(self, func: Callable) -> str:
        sig = inspect.signature(func)

        if sig.return_annotation != inspect.Signature.empty:
            return sig.return_annotation
        else:
            return None

    def _get_typingOrigin(self, return_type) -> bool:
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

    def _get_functionReturnType(self, func: Callable) -> Dict[str, Any]:
        return_caller = self._inspect_returnType(func)
        return_type = None

        if return_caller is not None:
            if self._get_typingOrigin(return_caller):
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

    def _attach_attributs(self, func: Callable, prototype: str):
        if "bound method" not in str(func):
            setattr(func, "__suggest__", enhance)
            setattr(func, "_prot", prototype)
