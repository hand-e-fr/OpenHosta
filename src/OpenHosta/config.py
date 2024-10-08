import sys
import requests
import json
import re
from jsonschema import validate
from pydantic import BaseModel
from typing import get_origin, get_args

from .errors import ApiKeyError


def is_valid_url(url):
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
        self.__last_request = None
        
        self.conversion_function = {
            str: lambda x: str(x),
            int: lambda x: int(x),
            float: lambda x: float(x),
            list: lambda x: list(x),
            set: lambda x: set(x),
            frozenset: lambda x: frozenset(x),
            tuple: lambda x: tuple(x),
            bool: lambda x: bool(x),
        }

        if any(var is None for var in (model, base_url)):
            sys.stderr.write(f"[CONFIG_ERROR] Empty values.")
            return
        elif not is_valid_url(self.base_url):
            sys.stderr.write(f"[CONFIG_ERROR] Invalid URL.")
            return

    def __str__(self) -> str:
        return (
            f"[OpenHosta] <{self.__class__.__module__}.{self.__class__.__name__} object at {hex(id(self))}>\n"
            f"Model: {self.model}\n"
            f"Base_url: {self.base_url}\n"
            "Infos:\n"
        )

    def api_call(
        self, sys_prompt: str, user_prompt: str, creativity: float, diversity: float
    )->requests.models.Response:
        if self.api_key is None or not self.api_key:
            raise ApiKeyError("Empty API key.")

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

        self.__last_request = l_body        

        try:
            response = requests.post(self.base_url, json=l_body, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            sys.stderr.write(f"\n[CALL_ERROR] Request failed:\n{e}\n\n")
        if response.status_code != 200:
            if "invalid_api_key" in str(response.text):
                raise ApiKeyError("Incorrect API key.")
            else:    
                sys.stderr.write(f"[CALL_ERROR] API call was unsuccessful.\nStatus code: {response.status_code}:\n{response.text}")
        return response

    def request_handler(self, response, return_type, return_caller):
        l_ret = ""

        data = response.json()
        json_string = data["choices"][0]["message"]["content"]

        try:
            l_ret_data = json.loads(json_string)
            # validate(
            #     instance=l_ret_data.get("return", {}),
            #     schema=return_type.get("properties", {}),
            # )  # Here

        except json.JSONDecodeError as e:
            sys.stderr.write(f"JSONDecodeError: {e}")
            l_cleand = "\n".join(json_string.split("\n")[1:-1])
            l_ret_data = json.loads(l_cleand)
            l_ret = l_ret_data["return"]
            return l_ret

        if "return_hosta_type" in return_type["properties"]:
            if return_caller in self.conversion_function:
                convert_function = self.conversion_function[return_caller]
                l_ret = convert_function(l_ret_data["return"])
            else:
                l_ret = l_ret_data["return"]

        elif "return_hosta_type_typing" in return_type["properties"]:
            l_ret = self.convert_to_type(l_ret_data["return"], return_caller)

        elif "return_hosta_type_any" in return_type["properties"]:
            l_ret = l_ret_data["return"]

        elif issubclass(return_caller, BaseModel):
            try:
                l_ret = return_caller(**l_ret_data["return"])
            except:
                sys.stderr.write("Unable t parse answer: ", l_ret_data["return"])
                for m in self.__last_request["messages"]:
                    sys.stderr.write(" "+m["role"]+">\n=======\n", m["content"][0]["text"])
                sys.stderr.write("Answer>\n=======\n",  l_ret_data["return"])
                lret = None

        else:
            l_ret = l_ret_data["return"]

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


__all__ = Model, set_default_apiKey, set_default_model, DefaultManager
