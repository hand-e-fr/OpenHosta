import requests
import json
import sys

from analytics import request_timer
from enhancer import enhance
from prompt import PromptMananger

_x = PromptMananger()

_emulator_pre_prompt = _x.get_prompt("emulate")

_g_apiKey = ""
_g_model = ""

def set_api_key(api_key):
    global _g_apiKey
    _g_apiKey = api_key

def set_model(model):
    global _g_model
    _g_model = model

@request_timer
def _exec_emulate(
    _function_doc=None,
    _function_call=None,
    _function_return=None,
    warn: bool = False,
    creativity: float = None,
    diversity: float = None,
):
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
                        + "\n---"
                        + "This need to return the following JSON format"+ str(_function_return) # Ajouté par Léandre
                        + "\n---"
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
        # print("json_string", json_string, flush=True)
        # print("json asked", _function_return, flush=True)
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


def thought(key):
    def inner_func(*args, **kwargs):
        try:
            result = _exec_emulate(_function_doc=key, _function_call=str(args[0]))
        except Exception as e:
            sys.stderr.write(Exception)
            sys.stderr.write("[LMDA_ERROR]")
            result = None
        return result

    return inner_func