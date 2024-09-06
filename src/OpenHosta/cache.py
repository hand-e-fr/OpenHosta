
import pickle
import os
import hashlib
import inspect
from typing import Callable, Dict, Any
from pydantic import BaseModel, create_model


CACHE_DIR = '__hostacache__'
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
            "function_call": "",
            "ho_example": [],
            "ho_example_id": 0,
            "ho_cothougt": [],
            "ho_cothougt_id": 0,
        }

    def __call__(self):
        func_name = self.func.__name__
        path_name = os.path.join(CACHE_DIR, f"{func_name}.openhc")


        if os.path.exists(path_name):
            with open(path_name, "rb") as f:
                cached_data = pickle.load(f)
            assert self.cache_id in cached_data, "Cache ID not found in cache file"
            
            if self._is_value_already_in_example(self.value, cached_data) == False:
                cached_data[str(self.cache_id)].append(self.value)
                cached_data[f'{str(self.cache_id)}'+'_id'] = self._get_hashFunction(str(cached_data[str(self.cache_id)]), 0, 0)
                cached_data["hash_function"] = self._get_hashFunction(cached_data["function_def"],
                                                                      cached_data["ho_example_id"],
                                                                      cached_data["ho_cothougt_id"])
                with open(path_name, "wb") as f:
                    pickle.dump(cached_data, f)
            return
        hosta_args = self._get_argsFunction(self.func)
        with open(path_name, "wb") as f:
            pickle.dump(hosta_args, f)
        return
        

    def _is_value_already_in_example(self, value, cached_data):
        for item in cached_data["ho_example"]:
            if isinstance(item, dict):
                if item == value:
                    return True
            elif isinstance(item, list):
                for sub_item in item:
                    if sub_item == value:
                        return True
        return False



    def _get_hashFunction(self, func_def: str, nb_example: int, nb_thought: int) -> str:
        combined = f"{func_def}{nb_example}{nb_thought}"
        return hashlib.md5(combined.encode()).hexdigest()

    def _get_argsFunction(self, func_obj):
        self.infos_cache["function_def"], func_prot = self._get_functionDef(func_obj)
        self.infos_cache["return_type"] = self._get_functionReturnType(func_obj)
        self.infos_cache[self.cache_id].append(self.value)
        self.infos_cache[f'{str(self.cache_id)}'+'_id'] = self._get_hashFunction(str(self.infos_cache[str(self.cache_id)]), 0, 0)
        self.infos_cache["hash_function"] = self._get_hashFunction(self.infos_cache["function_def"],
                                                                   self.infos_cache["ho_example_id"],
                                                                   self.infos_cache["ho_cothougt_id"])
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

