import pickle
import os
import hashlib
import inspect
from typing import Callable, Dict, Any, get_origin, get_args
import typing
import collections
from pydantic import BaseModel, create_model


CACHE_DIR = "__hostacache__"
os.makedirs(CACHE_DIR, exist_ok=True)


class Hostacache:
    def __init__(self, func, cache_id, value) -> None:
        self.func = func
        self.cache_id = cache_id
        self.value = value
        self.infos_cache = {
            "hash_function": "",
            "function_def": "",
            "return_type": "",
            "return_caller": "",
            "function_call": "",
            "function_args": {},
            "function_locals": {},
            "ho_example": [],
            "ho_example_id": 0,
            "ho_example_links": [],
            "ho_cothougt": [],
            "ho_cothougt_id": 0,
            "ho_data": [],
            "ho_data_id": 0,
        }

    def create_hosta_cache(self):
        func_name = self.func.__name__
        path_name = os.path.join(CACHE_DIR, f"{func_name}.openhc")


        if os.path.exists(path_name):
            with open(path_name, "rb") as f:
                cached_data = pickle.load(f)
                print(cached_data, flush=True)
            assert self.cache_id in cached_data, "Cache ID not found in cache file"


            if self._is_value_already_in_example(self.value, cached_data) == False:
                cached_data[str(self.cache_id)].append(self.value)
                cached_data[f"{str(self.cache_id)}" + "_id"] = self._get_hashFunction(
                    str(cached_data[str(self.cache_id)]), 0, 0
                )
                cached_data["hash_function"] = self._get_hashFunction(
                    cached_data["function_def"],
                    cached_data["ho_example_id"],
                    cached_data["ho_cothougt_id"],
                )
                with open(path_name, "wb") as f:
                    pickle.dump(cached_data, f)
                    print(cached_data, flush=True)

            return
        hosta_args = self._get_argsFunction(self.func)
        with open(path_name, "wb") as f:
            pickle.dump(hosta_args, f)
        return

    def _is_value_already_in_example(self, value, cached_data):
        if self.cache_id not in cached_data:
            print("Cache ID not found in cache file")
            return False

        def recursive_check(item, value):
            if isinstance(item, dict):
                # Check if the dict itself matches the value or if any key-value pair does
                if item == value or any(recursive_check(v, value) for v in item.values()):
                    return True
            elif isinstance(item, list):
                # Iterate through all items in the list (can be nested lists or dicts)
                return any(recursive_check(sub_item, value) for sub_item in item)
            else:
                # For non-list/dict items, check direct equality
                return item == value

        # Iterate through cached data for the cache_id
        for item in cached_data[self.cache_id]:
            if recursive_check(item, value):
                return True
        return False

    def _get_hashFunction(self, func_def: str, nb_example: int, nb_thought: int) -> str:
        combined = f"{func_def}{nb_example}{nb_thought}"
        return hashlib.md5(combined.encode()).hexdigest()

    def _get_argsFunction(self, func_obj):
        self.infos_cache["function_def"], func_prot = self._get_functionDef(func_obj)
        self.infos_cache["return_type"], self.infos_cache["return_caller"] = (
            self._get_functionReturnType(func_obj)
        )
        print(self.infos_cache, flush=True)
        print("*"*50)
        print(self.infos_cache[self.cache_id], flush=True)
        print(self.value, flush=True)
        self.infos_cache[self.cache_id].append(self.value)
        self.infos_cache[f"{str(self.cache_id)}" + "_id"] = self._get_hashFunction(
            str(self.infos_cache[str(self.cache_id)]), 0, 0
        )
        self.infos_cache["hash_function"] = self._get_hashFunction(
            self.infos_cache["function_def"],
            self.infos_cache["ho_example_id"],
            self.infos_cache["ho_cothougt_id"],
        )
        return self.infos_cache

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
