import inspect
import requests
import json
import sys
import os

from .analytics import request_timer
from .enhancer import _enhance

_exec_index: dict = {"auto": 0, "emulate": 1, "formulate": 2, "predict": 3, "build": 4}

class PromptMananger:
    def __init__(self, json_path=None):
        if json_path is None:
            try:
                self.path = os.path.join(os.path.dirname(__file__), 'prompt.json')
            except Exception as e:
                self.path = ""
                sys.stderr.write(f"[JSON_ERROR] Impossible to find prompt.json:\n{e}")
                return
        else:
            self.path = json_path
        
        try:
            with open(self.path, 'r', encoding="utf-8") as file:
                self.json = json.load(file)
                self.prompts = {item['key']: item for item in self.json['prompts']}
        except FileNotFoundError:
            sys.stderr.write(f"[JSON_ERROR] File not found: {self.path}\n")
            self.prompts = {}
        except json.JSONDecodeError as e:
            sys.stderr.write(f"[JSON_ERROR] JSON decode error:\n{e}\n")
            self.prompts = {}
            
    def get_prompt(self, key):
        prompt = self.prompts.get(key)
        if prompt:
            return prompt['text']
        sys.stderr.write(f"[JSON_ERROR] Prompt not found\n")
        return None

    def get_prompt_details(self, key):
        prompt = self.prompts.get(key)
        if prompt:
            return prompt
        sys.stderr.write(f"[JSON_ERROR] Prompt not found\n")
        return None

@request_timer
def emulate(
    _switch: bool = False,
    _function_doc=None,
    _function_call=None,
    warn: bool = False,
    creativity: float = None,
    diversity: float = None,
):
    if not _switch:
        global _exec_index
        return _exec_index["emulate"], warn, creativity, diversity
    else:
        global _emulator_pre_prompt, _g_model, _g_apiKey

        try:
            if not _emulator_pre_prompt or not _g_model or not _g_apiKey:
                raise ValueError("ValueError -> emulate empty values")

            if (creativity is not None and (creativity < 0 or creativity > 1)) or (
                diversity is not None and (diversity < 0 or diversity > 1)
            ):
                raise ValueError(
                    "ValueError -> emulate out of range values (0<creativity|diversity<1)"
                )
        except ValueError as v:
            sys.stderr.write(f"[EMULATE_ERROR]: {v}")
            return None

        api_key = _g_apiKey
        l_body = {
            "model": _g_model,
            "messages": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": _emulator_pre_prompt
                            + "---\n"
                            + str(_function_doc)
                            + "\n---",
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": str(_function_call)}],
                },
            ],
            "response_format": {"type": "json_object"},
            "temperature": creativity if creativity is not None else 0.7,
            "top_p": diversity if diversity is not None else 0.7,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions", json=l_body, headers=headers
        )

        __last_return__ = {"code": response.status_code, "text": response.text}

        __resp__ = response

        if response.status_code == 200:
            data = response.json()
            json_string = data["choices"][0]["message"]["content"]
            __last_content__ = json_string
            try:
                l_ret_data = json.loads(json_string)
                __jsonN__ = l_ret_data

            except json.JSONDecodeError as e:
                sys.stderr.write(f"JSONDecodeError: {e}")
                l_cleand = "\n".join(json_string.split("\n")[1:-1])
                l_ret_data = json.loads(l_cleand)

            __last_data__ = l_ret_data

            l_ret = l_ret_data["return"]
        else:
            sys.stderr.write(f"Error {response.status_code}: {response.text}")
            __last_data__ = {"return": None, "confidence": "low"}
            l_ret = None

        return l_ret

def pmac(func):

    def wrapper(*args, **kwargs):

        global _exec_index
        temp: tuple = ()

        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

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
        function_def = f"def {func_name}({func_params}):{func_return}\n    '''\n    {func.__doc__}\n    '''"

        func_call_args = ", ".join(
            [str(value) for value in bound_args.arguments.values()]
        )
        function_call = f"{func_name}({func_call_args})"

        wrapper.__prot__ = f"def {func_name}({func_params}):{func_return}"

        temp = func(*args, **kwargs)

        if temp[0] == _exec_index["emulate"]:
            try:
                result = emulate(
                    _switch=True,
                    _function_doc=function_def,
                    _function_call=function_call,
                    warn=temp[1],
                    creativity=temp[2],
                    diversity=temp[3],
                )
            except Exception as e:
                sys.stderr.write(Exception)
                sys.stderr.write(f"[EMU_ERROR] {e}", function_call)
                result = None
            return result
        else:
            sys.stderr.write("[PMAC_ERROR] Unknown index for execution.")
            return None

    wrapper.__suggest__ = _enhance
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper


def thought(key):
    def inner_func(*args, **kwargs):
        try:
            result = emulate(True, _function_doc=key, _function_call=str(args[0]))
        except Exception as e:
            sys.stderr.write(Exception)
            sys.stderr.write("[LMDA_ERROR]")
            result = None
        return result

    return inner_func
