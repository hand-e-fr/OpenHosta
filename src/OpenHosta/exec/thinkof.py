from __future__ import annotations

import json

from pydoc import locate

from ..core.config import DefaultPipeline
from ..core.logger import dialog_logger
from ..utils.errors import RequestError

def return_type(func):

    if not hasattr(func, "_infos"):
        raise AttributeError("Return type does not exist yet. This is likely because the function has never been called before.")

    return func._infos.f_type[1]

def gather_data_for_prompt_template(
        _infos
):    
    user_prompt_data = {
        "PRE_DEF":_infos.f_def,
        "PRE_TYPE": _infos.f_type[1],
        "PRE_SCHEMA": _infos.f_schema,
        "PRE_FUNCTION_CALL": _infos.f_call
    }
        
    return user_prompt_data

def guess_type(key: str, *args) -> object:
    l_default = DefaultPipeline.get_model()
    
    l_user_prompt = (
        "Function behavior: "
        + f"\"{key}\" applyed on "
        + f"{', '.join([str(arg) for arg in args])}\n"
    )

    response = l_default.api_call([
            {"role": "system", "content": """Say : Not implemented"""},
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
        l_ret =  await build_function_async(_model, _prompt, inner_func, key, args, kwargs, llm_args)
        return l_ret

    return inner_func

def thinkof(query_string, model=None, prompt=None, llm_args={}):
    
    def inner_func(*args, **kwargs):
        _model = model
        _prompt = prompt
        l_ret = build_function(_model, _prompt, inner_func, query_string, args, kwargs, llm_args)
        return l_ret

    return inner_func


def build_info(inner_func, query_string, *args, **kwargs):

    if not hasattr(inner_func, "_infos"):
        return_type = guess_type(query_string, *args, **kwargs)

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


    return _infos

async def build_function_async(model, prompt, inner_func, query_string, args, kwargs, llm_args):
        _model = model
        _prompt = prompt

        _infos = build_info(inner_func, query_string, *args, **kwargs)

        prompt_data = gather_data_for_prompt_template(_infos)
        prompt_data["PRE_FUNCTION_CALL"] = f"lambda_function('" + "', '".join(_infos.f_call) + "')"
        
        _model, _prompt = DefaultPipeline.outline(_model, _prompt, prompt_data)

        prompt_rendered = _prompt.render(prompt_data)

        logger = dialog_logger()
        logger.set_sys_prompt(prompt_rendered)
        logger.set_user_prompt(prompt_data["PRE_FUNCTION_CALL"])
  
        response_dict = await _model.api_call_async([
                {"role": "system", "content": prompt_rendered},
                {"role": "user", "content": prompt_data["PRE_FUNCTION_CALL"]}
            ],
            llm_args
        )
        
        logger.set_response_dict(response_dict)
        
        l_ret = _model.get_response_content(response_dict, _infos)
        l_data = _model.type_returned_data(l_ret, _infos)

        logger.set_response_data(l_data)

        return l_data

def build_function(model, prompt, inner_func, query_string, args, kwargs, llm_args):
        _model = model
        _prompt = prompt

        _infos = build_info(inner_func, query_string, *args, **kwargs)

        prompt_data = gather_data_for_prompt_template(_infos)
        prompt_data["PRE_FUNCTION_CALL"] = f"lambda_function('" + "', '".join(_infos.f_call) + "')"
        
        _model, _prompt = DefaultPipeline.outline(_model, _prompt, prompt_data)

        prompt_rendered = _prompt.render(prompt_data)

        logger = dialog_logger()
        logger.set_sys_prompt(prompt_rendered)
        logger.set_user_prompt(prompt_data["PRE_FUNCTION_CALL"])
  
        response_dict = _model.api_call([
                {"role": "system", "content": prompt_rendered},
                {"role": "user", "content": prompt_data["PRE_FUNCTION_CALL"]}
            ],
            llm_args
        )
        
        logger.set_response_dict(response_dict)
        
        l_ret = _model.get_response_content(response_dict, _infos)
        l_data = _model.type_returned_data(l_ret, _infos)

        logger.set_response_data(l_data)

        return l_data