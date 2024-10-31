import json
import sys
from typing import Callable

from .prompt import PromptMananger
from .config import DefaultManager


_x = PromptMananger()
_enhancer_pre_prompt = _x.get_prompt("enhance")

l_default = DefaultManager.get_default_model()


def _ai_call_enh(sys_prompt: str, func_prot: str, func_doc: str):
    global l_default

    l_user_prompt = (
        "\nHere's my python function's prototype:\n---\n"
        + func_prot
        + "\n---\n"
        + "\nHere's my python function's prompt:\n---\n"
        + func_doc
        + "\n---\n"
    )

    response = l_default.api_call(
        sys_prompt=sys_prompt, user_prompt=l_user_prompt, creativity=0.8, diversity=0.8
    )

    response_data = response.json()
    return response_data["choices"][0]["message"]["content"]


def _parse_data(response: str, last_enh: dict) -> dict:
    try:
        l_ret_data = json.loads(response)

    except json.JSONDecodeError as e:
        sys.stderr.write(f"JSONDecodeError: {e}")
        l_cleand = "\n".join(response.split("\n")[1:-1])
        l_ret_data = json.loads(l_cleand)

    last_enh["enhanced"] = l_ret_data["enhanced"]
    last_enh["review"] = l_ret_data["review"]
    last_enh["advanced"] = l_ret_data["advanced"]
    last_enh["mermaid"] = l_ret_data["mermaid"]
    return last_enh


def _build_attributes(func: object, last_enh) -> int:
    try:
        if not func.__name__ or not type(func.__name__) is str:
            raise ValueError("ValueError -> function name")
        if not last_enh["enhanced"] or not type(last_enh["enhanced"]) is str:
            raise ValueError("ValueError -> enhanced output")
        if not last_enh["review"] or not type(last_enh["review"]) is str:
            raise ValueError("ValueError -> review output")
        if not last_enh["advanced"] or not type(last_enh["advanced"]) is str:
            raise ValueError("ValueError -> seggested output")
        if not last_enh["mermaid"] or not type(last_enh["mermaid"]) is str:
            raise ValueError("ValueError -> mermaid output")
    except ValueError as e:
        sys.stderr.write(f"[BUILD_ERROR] {e}")
        return -1
    finally:
        func.enhanced_prompt = last_enh["enhanced"]
        func.review = last_enh["review"]
        func.advanced = last_enh["advanced"]
        func.diagram = last_enh["mermaid"]
    return 0


def enhance(func):
    global _enhancer_pre_prompt

    last_enh: dict = {
        "enhanced": None,
        "review": None,
        "advanced": None,
        "mermaid": None,
    }

    func_name, func_doc = func.__name__, func.__doc__

    last_return = _ai_call_enh(_enhancer_pre_prompt, func._prot, func_doc)

    last_enh = _parse_data(last_return, last_enh)

    _build_attributes(func, last_enh)
    return last_enh

def suggest(func:Callable):
    if not callable(func):
        raise ValueError("Suggest arguments must be a callable.")
    try:
        full = func.__suggest__(func)
    except AttributeError:
        raise AttributeError(f"The “__suggest__” attribute is not defined. The function {func.__name__} might not have been called.")
    return full
