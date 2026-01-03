from __future__ import annotations
from typing import Any, Dict, List, Set, Tuple

import os
import requests

from ..core.inspection import Inspection
from ..core.base_model import Model, ModelCapabilities
from ..core.errors import ApiKeyError, RequestError, RateLimitError

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
            retry_delay:int = None,            
        ):     
        super().__init__(
            max_async_calls=max_async_calls,
            additionnal_headers=additionnal_headers,
            api_parameters=api_parameters,
            retry_delay=retry_delay
        )

        self.reasoning_start_and_stop_tags = ["<think>", "</think>"]
        self.model_name = model_name
        self.set_api_url(base_url, model_name, chat_completion_url)
        self.api_key = api_key
        self.timeout = timeout

        self.capabilities = capabilities

        self._used_tokens = 0
        self._nb_requests = 0

        if any(var is None for var in (model_name, base_url)):
            raise ValueError(f"[Model.__init__] Missing values.")
    
    def set_api_url(self, url: str, model_name: str, chat_completions_url: str = "/chat/completions"):
        # Handle Azure case
        
        schema, hostname, route, route_extention, query = None, None, None, None, None
        
        if "://" in url:
            schema, url = url.split("://")
            schema = schema + "://"
        else:
            schema = "http://"
        
        if '?' in url:
            url, query = url.split("?")
            query = "?"+query
        else:
            query = ""
            
        if chat_completions_url in url:
            url, route_extention = url.split(chat_completions_url)
            route_extention = chat_completions_url + route_extention
        else:
            route_extention = chat_completions_url
            
        if "/" in url:
            parts = url.split("/")
            hostname = parts[0]
            route = "/"+"/".join(parts[1:])                
        elif "127.0.0.1:11434" in url:
            # Ollama detection
            hostname = url
            route = "/api/v1"
        elif "127.0.0.1:8000" in url:
            # Vllm detection
            hostname = url
            route = "/v1"
        else:
            route = ""

        if "openai.azure.com" in hostname:
            fix_azure_route = False
            if route == "":
                fix_azure_route = True
                route = "/openai/deployments/" + model_name
            if query == "":
                fix_azure_route = True
                query = "?api-version=2025-01-01-preview"

            if fix_azure_route:
                print(f"[OpenHosta] Fixing Azure route to: {schema}{hostname}{route}{route_extention}{query}")
       
        self.base_url = schema+hostname
        self.chat_completion_url = route + route_extention + query
    
    def api_call_without_retry(
        self,
        messages: List[Dict[str, str]],
        llm_args:Dict = {}
    ) -> Dict:

        if "force_json_output" in llm_args and ModelCapabilities.JSON_OUTPUT not in self.capabilities:
            llm_args.pop("force_json_output")

        api_key = self.api_key
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")

        # Typical error from begginers
        if api_key is None and "api.openai.com/v1" in self.base_url:
            raise ApiKeyError("[model.api_call_without_retry] Empty API key.")
        
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


        if "Retry-After" in response.headers:
            self.set_next_rate_limit(
                next_authorized_api_call_time=int(response.headers["Retry-After"]))
        elif 'x-ratelimit-reset-requests' in response.headers:
            self.set_next_rate_limit(
                next_authorized_api_call_time=int(response.headers['x-ratelimit-reset-requests']))
            
        if response.status_code == 200:
            pass
        elif response.status_code == 429:
            # print headers for debug
            raise RateLimitError(f"[Model.api_call_without_retry] Rate limit exceeded (HTTP 429). {response.text}")
        elif response.status_code == 401:
            raise ApiKeyError(f"[Model.api_call_without_retry] Unauthorized (HTTP 401). Check your API key. {response.text}")
        else:
            raise RequestError(f"[Model.api_call_without_retry] Request failed with status code {response.status_code}:\nAPI URL: {full_url}\n{response.text}\n\n")
            
        self._nb_requests += 1
        response_dict = response.json()
    
        return response_dict
    
    def models_on_same_api(self) -> List[str]:
        """
        List all models available on the same API.
        
        Returns:
            List[str]: List of model names.
        """

        api_key = self.api_key
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")

        # Typical error from begginers
        if api_key is None and "api.openai.com/v1" in self.base_url:
            raise ApiKeyError("[model.models_on_same_api] Empty API key.")
        
        headers = {
            "Content-Type": "application/json"
        }

        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        for key, value in self.additionnal_headers.items():
            headers[key] = value
        
        full_url = f"{self.base_url}/models"
        
        response = requests.get(full_url, headers=headers, timeout=self.timeout)
        
        if not response.ok:
            raise RequestError(f"[Model.get_available_model_names] Request failed with status code {response.status_code}:\n{response.text}\n\n")
        
        model_list = []
        if "data" in response.json():
            for model in response.json()["data"]:
                if model["object"] == "model":
                    model_list.append(model["id"])
                else:
                    print(f"Ignoring {model["id"]}:", model)
            
        return model_list
    
    def get_consumption(self, response_dict) -> dict:
        if "usage" in response_dict:
            self._used_tokens += int(response_dict["usage"]["total_tokens"])

    def get_response_content(self, response_dict: Dict) -> str:
        
        assert "choices" in response_dict, f"[Model.get_response_content] Invalid response: {response_dict}"
        assert len(response_dict["choices"]) > 0, f"[Model.get_response_content] Invalid response: {response_dict}"
        assert "message" in response_dict["choices"][0], f"[Model.get_response_content] Invalid response: {response_dict}"

        if "text" in response_dict["choices"][0]["message"]:
            response = response_dict["choices"][0]["message"]["text"]
        
        elif "content" in response_dict["choices"][0]["message"]:
            response = response_dict["choices"][0]["message"]["content"]
            
        else:
            response = ""

        return response
    
        
    def get_thinking_and_data_sections(
                        self,
                        response:str, 
                        reasoning_start_and_stop_tags = ["<think>", "</think>"]) -> Tuple[str, str]:
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
        

    def print_last_prompt(self, inspection:Inspection):
        """
        Print the last prompt sent to the LLM when using function `function_pointer`.
        """
        if "llm_api_messages_sent" in inspection.logs and \
            len(inspection.logs["llm_api_messages_sent"]) >= 1:
            print("\nSystem prompt:\n-----------------")
            print(inspection.logs["llm_api_messages_sent"][0]["content"][0]["text"])
        if "llm_api_messages_sent" in inspection.logs and \
            len(inspection.logs["llm_api_messages_sent"]) >= 2:
            print("\nUser prompt:\n-----------------")
            print(inspection.logs["llm_api_messages_sent"][1]["content"][0]["text"])
        if "rational" in inspection.logs and inspection.logs["rational"]:
            print("\nRational:\n-----------------")
            print(inspection.logs["rational"])
        if "llm_api_response" in inspection.logs and \
            "choices" in inspection.logs["llm_api_response"] and \
                len(inspection.logs["llm_api_response"]["choices"]) >= 1:
            print("\nLLM response:\n-----------------")
            print(inspection.logs["llm_api_response"]["choices"][0]["message"]["content"])

