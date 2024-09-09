import sys

from emulate import _exec_emulate
from config import DefaultManager
from prompt import PromptMananger

l_default = DefaultManager.get_default_model()
_x = PromptMananger()
_thought_sys_prompt = _x.get_prompt("thought")

g_return_type = ""

def thought(key):
    global g_return_type
    _function_infos = {
        "function_def": "",
        "function_call": "",
        "return_type": None,
        "return_type": None,
        "ho_example": None,
        "function_locals": None
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
        g_return_type = data["choices"][0]["message"]["content"]
        
        typed = (
            str(args)
            + "\n"
            + "Here's the return type that must respect for your response. The python type is in the key \"type\" of this JSON schema:\n"
            + g_return_type
            + "\n"
        )
        
        try:
            _function_infos["function_def"] = key
            _function_infos["function_call"] = typed
            result = _exec_emulate(_function_infos)
        except Exception as e:
            sys.stderr.write(f"{e}")
            sys.stderr.write("[LMDA_ERROR]")
            result = None
        return result

    setattr(inner_func, "_return_type", g_return_type)
    return inner_func
