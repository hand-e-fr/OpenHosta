from __future__ import annotations

import sys
import requests
from requests.exceptions import RequestException
from requests.models import Response
import json
import re
from pydantic import BaseModel
from typing import get_origin, get_args, Any, Optional

from .errors import ApiKeyError, RequestError
from .hosta import Func

def is_valid_url(url:str)->bool:
    regex = re.compile(
        r"^(?:http|ftp)s?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
        r"\[?[A-F0-9]*:[A-F0-9:]+\]?)"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return re.match(regex, url) is not None

class Model:

    _SYS_PROMPT = ""

    def __init__(self, model: str = None, base_url: str = None, api_key: str = None):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self._last_request = None
        self._used_tokens = 0
        self._nb_requests = 0

        if any(var is None for var in (model, base_url)):
            raise ValueError(f"[Model.__init__] Missing values.")
        elif not is_valid_url(self.base_url):
            raise ValueError(f"[Model.__init__] Invalid URL.")

    def api_call(
        self,
        sys_prompt: str,
        user_prompt: str,
        creativity: Optional[float],
        diversity: Optional[float]
    )->Response:
        if self.api_key is None or not self.api_key:
            raise ApiKeyError("[model.api_call] Empty API key.")

        l_body = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": sys_prompt}],
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": user_prompt}],
                },
            ],
            "response_format": {"type": "json_object"},
            "temperature": creativity if creativity is not None else 0.7,
            "top_p": diversity if diversity is not None else 0.7,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        self._last_request = l_body        

        try:
            response = requests.post(self.base_url, json=l_body, headers=headers)
            response.raise_for_status()
        except RequestException as e:
            RequestException(f"[Model.api_call] Request failed:\n{e}\n\n")
        if response.status_code != 200:
            if "invalid_api_key" in str(response.text):
                raise ApiKeyError("[Model.api_call] Incorrect API key.")
            else:    
                raise RequestError(f"[Model.api_call] API call was unsuccessful.\nStatus code: {response.status_code}:\n{response.text}")
        self._nb_requests += 1
        return response

    def request_handler(self, response:Response, func:Func)->Any:
        l_ret = None
            
        data = response.json()
        json_string = data["choices"][0]["message"]["content"]
        if "usage" in data:
            self._used_tokens += int(data["usage"]["total_tokens"])
        try:
            l_ret_data = json.loads(json_string)
        except json.JSONDecodeError as e:
            sys.stderr.write(f"[Model.request_handler] JSONDecodeError: {e}\nContinuing the process.")
            l_cleand = "\n".join(json_string.split("\n")[1:-1])
            l_ret_data = json.loads(l_cleand)
        l_ret = l_ret_data["return"]
        print(f"TYPE: {func.f_type[1]}")
        if func.f_type[1] is not None:
            if issubclass(func.f_type[1], BaseModel):
                try:
                    l_ret = func.f_type[1](**l_ret)
                    print(type(l_ret))
                except:
                    l_ret = l_ret_data["return"]
        # if "return_hosta_type" in return_type["properties"]:
        #     if return_caller in self.conversion_function:
        #         convert_function = self.conversion_function[return_caller]
        #         if l_ret_data["return"] is not None:
        #             l_ret = convert_function(l_ret_data["return"])
        #     else:
        #         l_ret = l_ret_data["return"]
        # elif "return_hosta_type_typing" in return_type["properties"]:
        #     l_ret = self.convert_to_type(l_ret_data["return"], return_caller)
        # elif issubclass(return_caller, BaseModel):
        #     try:
        #         l_ret = return_caller(**l_ret_data["return"])
        #     except:
        #         sys.stderr.write("Unable to parse answer: ", l_ret_data["return"])
        #         for m in self._last_request["messages"]:
        #             sys.stderr.write(" "+m["role"]+">\n=======\n", m["content"][0]["text"])
        #         sys.stderr.write("Answer>\n=======\n",  l_ret_data["return"])
        #         l_ret = None
        # else:
        #     l_ret = l_ret_data["return"]
        return l_ret

    def convert_to_type(self, data, type):
        origin = get_origin(type)
        args = get_args(type)

        if origin != None:
            if origin in self.conversion_function:
                convert_function = self.conversion_function[origin]
                return convert_function(self.convert_to_type(d, args[0]) for d in data)

        return data


class DefaultModel:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DefaultModel, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "model"):
            self.model = None

    def set_default_model(self, new):
        if isinstance(new, Model):
            self.model = new
        else:
            sys.stderr.write("[CONFIG_ERROR] Invalid model instance.\n")

    def set_default_apiKey(self, api_key=None):
        if api_key is not None or isinstance(api_key, str):
            self.model.api_key = api_key
        else:
            sys.stderr.write("[CONFIG_ERROR] Invalid API key.")

    def get_default_model(self):
        return self.model


DefaultManager = DefaultModel()


def set_default_model(new):
    DefaultManager.set_default_model(new)


def set_default_apiKey(api_key=None):
    DefaultManager.set_default_apiKey(api_key)
