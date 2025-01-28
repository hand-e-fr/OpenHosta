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
            force_json_output:bool = True,
            additionnal_headers: Dict[str, Any] = {}
        ):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.user_headers = additionnal_headers
        self.json_form = force_json_output
        self._used_tokens = 0
        self._nb_requests = 0

        if any(var is None for var in (model, base_url)):
            raise ValueError(f"[Model.__init__] Missing values.")
        elif not is_valid_url(self.base_url):
            raise ValueError(f"[Model.__init__] Invalid URL.")

    def api_call(
        self,
        messages: list[dict[str, str]],
        json_form: bool = None,
        **llm_args
    ) -> Dict:
        if json_form is None:
            json_form = self.json_form

        if self.api_key is None or not self.api_key:
            raise ApiKeyError("[model.api_call] Empty API key.")

        l_body = {
            "model": self.model,
            "messages": messages,
        }
        headers = {
            "Content-Type": "application/json"
        }
        
        if "azure.com" in self.base_url:
            headers["api-key"] = f"{self.api_key}"
        else:
            headers["Authorization"] = f"Bearer {self.api_key}"

        for key, value in self.user_headers.items():
            headers[key] = value
 
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

    def request_handler(self, response_dict: Dict, func: Func) -> Any:

        if "usage" in response_dict:
            self._used_tokens += int(response_dict["usage"]["total_tokens"])

        response = response_dict["choices"][0]["message"]["content"]
        rational, answer = self.split_cot_answer(response)

        func.f_obj._last_response["rational"] = rational
        func.f_obj._last_response["answer"] = answer
        
        response = self.extract_json(answer)
        
        try:
            l_ret_data = json.loads(response)
        except json.JSONDecodeError as e:
            sys.stderr.write(
                f"[Model.request_handler] JSONDecodeError: {e}\nContinuing the process.")
            l_ret_data = ""

        return HostaChecker(func, l_ret_data).check()

    def split_cot_answer(self, response:str) -> tuple[str, str]:
        """
        This function split response into rational and answer.

        Special prompt may ask for chain-of-thought or models might be trained to reason first.

        Args:
            response (str): response from the model.

        Returns:
            tuple[str, str]: rational and answer.
        """
        response = response.strip()

        if response.startswith("<think>") and "</think>" in response:
            chunks = response[8:].split("</think>")
            rational = chunks[0]
            answer = "</think>".join(chunks[1:]) # in case there are multiple </think> tags
        else:
            rational, answer = "", response
        
        return rational, answer


    def extract_json(self, response: str) -> str:
        """
        Extracts the JSON part from the response.

        Some LLM will return the JSON with some additional text.
        """
        if response.strip().endswith("```"):
            chuncks = response.split("```")
            last_chunk = chuncks[-2]
            if "{" in last_chunk and "}" in last_chunk:
                chunk_lines = last_chunk.split("\n")[1:]
                # find first line with { and last line with }
                start_line = next(i for i, line in enumerate(chunk_lines) if "{" in line)
                end_line = len(chunk_lines) - next(i for i, line in enumerate(reversed(chunk_lines)) if "}" in line) - 1
                response = "\n".join(chunk_lines[start_line:end_line + 1])

            else:
                sys.stderr.write(
                    f"[Model.extract_json] JSON not found in the response. (passthrough)")
        
        return response

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
