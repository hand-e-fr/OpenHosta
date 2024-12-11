from __future__ import annotations

import sys
import json
import re
import sys
import requests
from typing import Any, Dict

from .checker import HostaChecker
from .pydantic_usage import Func
from ..utils.errors import ApiKeyError, RequestError


def is_valid_url(url: str) -> bool:
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

    def __init__(self, 
            model: str = None, 
            base_url: str = None, 
            api_key: str = None, 
            timeout: int = 30,
            additionnal_headers: Dict[str, Any] = {}
        ):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.user_headers = additionnal_headers
        self._last_request = None
        self._used_tokens = 0
        self._nb_requests = 0

        if any(var is None for var in (model, base_url)):
            raise ValueError(f"[Model.__init__] Missing values.")
        elif not is_valid_url(self.base_url):
            raise ValueError(f"[Model.__init__] Invalid URL.")

    def api_call(
        self,
        messages: list[dict[str, str]],
        json_form: bool = True,
        **llm_args
    ) -> Dict:
        if self.api_key is None or not self.api_key:
            raise ApiKeyError("[model.api_call] Empty API key.")

        l_body = {
            "model": self.model,
            "messages": messages,
        }
        headers = {
            "Content-Type": "application/json"
        }
        
        for key, value in self.user_headers.items():
            headers[key] = value
            
        if "azure.com" in self.base_url:
            headers["api-key"] = f"{self.api_key}"
        else:
            headers["Authorization"] = f"Bearer {self.api_key}"
 
        if json_form:
            l_body["response_format"] = {"type": "json_object"}
        for key, value in llm_args.items():
            l_body[key] = value
        try:
            response = requests.post(self.base_url, headers=headers, json=l_body, timeout=self.timeout)

            if response.status_code  != 200:
                response_text = response.text
                if "invalid_api_key" in response_text:
                    raise ApiKeyError("[Model.api_call] Incorrect API key.")
                else:
                    raise RequestError(
                        f"[Model.api_call] API call was unsuccessful.\n"
                        f"Status code: {response.status_code }:\n{response_text}"
                    )
            self._nb_requests += 1
            return response.json()
        except Exception as e:
            raise RequestError(f"[Model.api_call] Request failed:\n{e}\n\n")

    def request_handler(self, response: Dict, func: Func) -> Any:
        json_string = response["choices"][0]["message"]["content"]
        if "usage" in response:
            self._used_tokens += int(response["usage"]["total_tokens"])
        try:
            l_ret_data = json.loads(json_string)
        except json.JSONDecodeError as e:
            sys.stderr.write(
                f"[Model.request_handler] JSONDecodeError: {e}\nContinuing the process.")
            l_cleand = "\n".join(json_string.split("\n")[1:-1])
            l_ret_data = json.loads(l_cleand)
        return HostaChecker(func, l_ret_data).check()


class DefaultModel:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DefaultModel, cls).__new__(
                cls, *args, **kwargs)
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

# anntations, errors handling, doc, all
