from __future__ import annotations

import json
import asyncio

from pydoc import locate

from ..core.config import DefaultModelPolicy
from ..core.hosta_inspector import FunctionMetadata
from ..utils.errors import RequestError
from ..utils.meta_prompt import THOUGHT_PROMPT

def gather_data_for_prompt_template(
        _infos: FunctionMetadata
):    
    user_prompt_data = {
        "PRE_DEF":_infos.f_def,
        "PRE_TYPE": _infos.f_type[1],
        "PRE_SCHEMA": _infos.f_schema,
        "PRE_FUNCTION_CALL": _infos.f_call
    }
        
    return user_prompt_data

async def guess_type(key: str, *args) -> object:
    l_default = DefaultModelPolicy.get_model()
    
    l_user_prompt = (
        "Function behavior: "
        + f"\"{key}\" applyed on "
        + f"{', '.join([str(arg) for arg in args])}\n"
    )

    response = await l_default.api_call_async([
            {"role": "system", "content": THOUGHT_PROMPT.render()},
            {"role": "user", "content": l_user_prompt}
        ],
        llm_args={"temperature":0.2},
    )

    type_json = response["choices"][0]["message"]["content"]
    type_dict = json.loads(type_json)
    type_str = str(type_dict["type"])
    type_object = locate(type_str)
    return type_object


def thinkof_async(key, model=None, prompt=None, llm_args={}):
    
    async def inner_func(*args, **kwargs):
        _model = model
        _prompt = prompt
        l_ret =  await build_function(_model, _prompt, inner_func, key, args, kwargs, llm_args)
        return l_ret

    return inner_func


def thinkof(query_string, model=None, prompt=None, llm_args={}):
    
    def inner_func(*args, **kwargs):
        _model = model
        _prompt = prompt
        l_ret = asyncio.run(build_function(_model, _prompt, inner_func, query_string, args, kwargs, llm_args))
        return l_ret

    return inner_func


async def build_function(model, prompt, inner_func, query_string, args, kwargs, llm_args):
        _model = model
        _prompt = prompt

        if not hasattr(inner_func, "_infos"):
            return_type = await guess_type(query_string, *args, **kwargs)

            _infos = FunctionMetadata()
            _infos.f_schema = {"type": f"{return_type.__name__}"}
            _infos.f_def = f'''
```python
def lambda_function(*argument)->{return_type.__name__}:
    """
    {query_string}
    """
    ...
```
'''
            _infos.f_call = [str(arg) for arg in args]
            _infos.f_type = ([], return_type)
            setattr(inner_func, "_infos", _infos)
        else:
            _infos = getattr(inner_func, "_infos")

        prompt_data = gather_data_for_prompt_template(_infos)
        prompt_data["PRE_FUNCTION_CALL"] = f"lambda_function('" + "', '".join(_infos.f_call) + "')"

        if _model is None:
            _model = DefaultModelPolicy.get_model()

        if _prompt is None:
            _prompt = DefaultModelPolicy.get_prompt()

        prompt_rendered = _prompt.render(prompt_data)

        logging_object = { 
            "_last_request": {},
            "_last_response": {}
        }

        setattr(inner_func, "_last_request", logging_object["_last_request"])

        logging_object["_last_request"]['sys_prompt']=prompt_rendered
        logging_object["_last_request"]['user_prompt']=prompt_data["PRE_FUNCTION_CALL"]
        
        try:
            response_dict = await _model.api_call_async([
                    {"role": "system", "content": prompt_rendered},
                    {"role": "user", "content": prompt_data["PRE_FUNCTION_CALL"]}
                ],
                llm_args
            )
            
            logging_object["_last_response"]["response_dict"] = response_dict
            
            l_ret = _model.response_parser(response_dict, _infos)
            l_data = _model.type_returned_data(l_ret, _infos)

            logging_object["_last_response"]["data"] = l_data
            setattr(inner_func, "_last_response", logging_object["_last_response"])

        except Exception as e:
            raise RequestError(f"[thinkof] Cannot emulate the function.\n{e}")
        return l_data