from __future__ import annotations
from typing import Any, Dict, Set

import os
import requests

from ..models import Model, ModelCapabilities
from ..utils.errors import ApiKeyError, RequestError

class OpenAICompatibleModel(Model):

    def __init__(self, 
            model_name: str = None, 
            max_async_calls = 7,
            additionnal_headers: Dict[str, Any] = {},
            api_parameters:Dict[str, Any] = {},
            capabilities:Set[ModelCapabilities] = {ModelCapabilities.TEXT2TEXT},
            base_url: str = None, 
            chat_completion_url: str = "/chat/completions",
            api_key: str = None, 
            timeout: int = 30,
        ):     
        super().__init__(
            max_async_calls=max_async_calls,
            additionnal_headers=additionnal_headers,
            api_parameters=api_parameters,
        )

        self.reasoning_start_and_stop_tags = ["<think>", "</think>"]
        self.model_name = model_name
        self.base_url = base_url
        self.chat_completion_url = chat_completion_url if not self.base_url.endswith(chat_completion_url) else ""
        self.api_key = api_key
        self.timeout = timeout

        self.capabilities = capabilities

        self._used_tokens = 0
        self._nb_requests = 0

        if any(var is None for var in (model_name, base_url)):
            raise ValueError(f"[Model.__init__] Missing values.")
    
    def api_call(
        self,
        messages: list[dict[str, str]],
        llm_args:dict = {}
    ) -> Dict:

        if "force_json_output" in llm_args and ModelCapabilities.JSON_OUTPUT not in self.capabilities:
            llm_args.pop("force_json_output")

        api_key = self.api_key
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")

        # Typical error from begginers
        if api_key is None and "api.openai.com/v1" in self.base_url:
            raise ApiKeyError("[model.api_call] Empty API key.")
        
        l_body = {
            "model": self.model_name,
            "messages": messages,
        }
        headers = {
            "Content-Type": "application/json"
        }
        
        if "azure.com" in self.base_url:
            headers["api-key"] = f"{api_key}"
        else:
            headers["Authorization"] = f"Bearer {api_key}"

        for key, value in llm_args.items():
            if key == "force_json_output" and value:
                l_body["response_format"] = {"type": "json_object"}
            else:
                l_body[key] = value
        try:
            full_url = f"{self.base_url}{self.chat_completion_url}"

            response = requests.post(full_url, headers=headers, json=l_body, timeout=self.timeout)

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
            response_dict = response.json()
        
        except Exception as e:
            print(f"[Model.api_call] Request failed:\n{e}\n\n")
            raise e

        return response_dict
    
    def get_consumption(self, response_dict) -> dict:
        if "usage" in response_dict:
            self._used_tokens += int(response_dict["usage"]["total_tokens"])

    def get_response_content(self, response_dict: Dict) -> str:

        response = response_dict["choices"][0]["message"]["content"]

        if "text" in response_dict["choices"][0]["message"]:
            response = response_dict["choices"][0]["message"]["text"]

        return response