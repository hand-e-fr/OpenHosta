from __future__ import annotations
from typing import Any, Dict, Set

import os
import requests

from ..core.inspection import Inspection
from ..models import Model, ModelCapabilities
from ..utils.errors import ApiKeyError, RequestError, RateLimitError

class OpenAICompatibleModel(Model):

    def __init__(self, 
            model_name: str = None, 
            max_async_calls = 7,
            additionnal_headers: Dict[str, Any] = {},
            api_parameters:Dict[str, Any] = {},
            capabilities:Set[ModelCapabilities] = {ModelCapabilities.TEXT2TEXT},
            base_url: str = "https://api.openai.com/v1", 
            chat_completion_url: str = "/chat/completions",
            api_key: str = None, 
            timeout: int = 60,
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

        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        for key, value in self.additionnal_headers.items():
            headers[key] = value

        all_api_parameters = self.api_parameters | llm_args
        for key, value in all_api_parameters.items():
            if key == "force_json_output" and value:
                l_body["response_format"] = {"type": "json_object"}
            else:
                l_body[key] = value
        
        full_url = f"{self.base_url}{self.chat_completion_url}"

        response = requests.post(full_url, headers=headers, json=l_body, timeout=self.timeout)

        if response.status_code == 200:
            pass
        elif response.status_code == 429:
            raise RateLimitError(f"[Model.api_call] Rate limit exceeded (HTTP 429). {response.text}")
        elif response.status_code == 401:
            raise ApiKeyError(f"[Model.api_call] Unauthorized (HTTP 401). Check your API key. {response.text}")
        else:
            raise RequestError(f"[Model.api_call] Request failed with status code {response.status_code}:\n{response.text}\n\n")
            
        self._nb_requests += 1
        response_dict = response.json()
    
        return response_dict
    
    def get_consumption(self, response_dict) -> dict:
        if "usage" in response_dict:
            self._used_tokens += int(response_dict["usage"]["total_tokens"])

    def get_response_content(self, response_dict: Dict) -> str:

        response = response_dict["choices"][0]["message"]["content"]

        if "text" in response_dict["choices"][0]["message"]:
            response = response_dict["choices"][0]["message"]["text"]

        return response
    
        
    def get_thinking_and_data_sections(
                        self,
                        response:str, 
                        reasoning_start_and_stop_tags = ["<think>", "</think>"]) -> tuple[str, str]:
        """
        This function split response into rational and answer.

        Special prompt may ask for chain-of-thought or models might be trained to reason first.

        Args:
            response (str): response from the model.

        Returns:
            tuple[str, str]: rational and answer.
        """
        rational = ""
        answer = ""

        response = response.strip()
        if reasoning_start_and_stop_tags[0] in response and reasoning_start_and_stop_tags[1] in response:
            chunks = response[8:].split(reasoning_start_and_stop_tags[1])
            rational += chunks[0]
            answer += reasoning_start_and_stop_tags[1].join(chunks[1:]) # in case there are multiple </think> tags
        else:
            answer += response
        
        return rational, answer
        

    def print_last_prompt(self, hosta_inspection:Inspection):
        """
        Print the last prompt sent to the LLM when using function `function_pointer`.
        """
        if "llm_api_messages_sent" in hosta_inspection['logs'] and \
            len(hosta_inspection['logs']["llm_api_messages_sent"]) >= 1:
            print("\nSystem prompt:\n-----------------")
            print(hosta_inspection['logs']["llm_api_messages_sent"][0]["content"][0]["text"])
        if "llm_api_messages_sent" in hosta_inspection['logs'] and \
            len(hosta_inspection['logs']["llm_api_messages_sent"]) >= 2:
            print("\nUser prompt:\n-----------------")
            print(hosta_inspection['logs']["llm_api_messages_sent"][1]["content"][0]["text"])
        if "rational" in hosta_inspection['logs'] and hosta_inspection['logs']["rational"]:
            print("\nRational:\n-----------------")
            print(hosta_inspection['logs']["rational"])
        if "llm_api_response" in hosta_inspection['logs'] and \
            "choices" in hosta_inspection['logs']["llm_api_response"] and \
                len(hosta_inspection['logs']["llm_api_response"]["choices"]) >= 1:
            print("\nLLM response:\n-----------------")
            print(hosta_inspection['logs']["llm_api_response"]["choices"][0]["message"]["content"])

