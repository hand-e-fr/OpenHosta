import sys
import json
from pydoc import locate
from pydantic import create_model

from ..core.emulate import _exec_emulate
from ..core.config import DefaultManager
from ..utils.prompt import PromptMananger

l_default = DefaultManager.get_default_model()
_x = PromptMananger()
_thought_sys_prompt = _x.get_prompt("thought")


def thought(key):
    _function_infos = {
        "function_def": "",
        "function_call": "",
        "return_type": None,
        "return_type": None,
        "ho_example": None,
        "function_locals": None,
        "return_caller": None,
    }

    def inner_func(*args, **kwargs):
        global l_default, _thought_sys_prompt

        l_user_prompt = (
            "Here's the function behavior:\n"
            + f"{key}\n"
            + "Here's the arguments:\n"
            + f"{args}\n"
        )

        response = l_default.api_call(
            sys_prompt=_thought_sys_prompt,
            user_prompt=l_user_prompt,
            creativity=0.5,
            diversity=0.5,
        )

        data = response.json()
        type_json = data["choices"][0]["message"]["content"]
        type_dict = json.loads(type_json)
        type_str = str(type_dict["type"])

        _function_infos["return_caller"] = locate(type_str)
        setattr(inner_func, "_return_type", _function_infos["return_caller"])

        new_model = create_model(
            "Hosta_return_shema",
            return_hosta_type=(_function_infos["return_caller"], ...),
        )
        _function_infos["return_type"] = new_model.model_json_schema()

        typed = (
            str(args)
            + "\n"
            + 'Here\'s the return type that must respect for your response. The python type is in the key "type" of this JSON schema:\n'
            + str(type_dict)
            + "\n"
        )

        try:
            _function_infos["function_def"] = key
            _function_infos["function_call"] = typed
            result = _exec_emulate(_function_infos, inner_func)
        except Exception as e:
            sys.stderr.write(f"{e}")
            sys.stderr.write("[LMDA_ERROR]")
            result = None
        return result

    return inner_func

def tmp():
    x = thought("add two")
    x(4)
    x(4)
    x(7)
    x = thought("Salut je suis un fermier ! Raconte moi une histoire")
    y = thought("add two")
 
 