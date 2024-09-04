import requests
import json
import sys

from prompt import PromptMananger
from config import DefaultManager


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
    
    response = l_default._api_call(
        sys_prompt=sys_prompt, 
        user_prompt=l_user_prompt, 
        creativity=0.8, 
        diversity=0.8
    )

    response_data = response.json()
    print(response_data["choices"][0]["message"]["content"])
    return response_data["choices"][0]["message"]["content"]
    


def _parse_data(response: str, last_enh: dict) -> dict:
    current_section = None
    current_text = []

    for line in response.splitlines():
        if line.startswith("->"):
            if current_section:
                last_enh[current_section] = "\n".join(current_text).strip()
            current_section = line[3:].strip(":")
            current_text = []
        else:
            current_text.append(line)
    if current_section:
        last_enh[current_section] = "\n".join(current_text).strip()
    return last_enh


def _build_attributes(func: object, last_enh) -> int:
    try:
        if not func.__name__ and not type(func.__name__) is str:
            raise ValueError("ValueError -> function name")
        if not last_enh["enhanced"] and not type(last_enh["enhanced"]) is str:
            raise ValueError("ValueError -> enhanced output")
        if not last_enh["review"] and not type(last_enh["review"]) is str:
            raise ValueError("ValueError -> review output")
        if not last_enh["advanced"] and not type(last_enh["advanced"]) is str:
            raise ValueError("ValueError -> seggested output")
        if not last_enh["mermaid"] and not type(last_enh["mermaid"]) is str:
            raise ValueError("ValueError -> mermaid output")
    except ValueError as e:
        sys.stderr.write(f"[BUILD_ERROR] {e}")
        return -1
    finally:
        func.enhanced_prompt = last_enh["enhanced"]
        func.review = last_enh["review"]
        func.advanced = last_enh["advanced"]
        func.diagramm = last_enh["mermaid"]
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
