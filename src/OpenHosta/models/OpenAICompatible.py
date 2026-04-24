from __future__ import annotations
from typing import Any, Dict, List, Set, Tuple

import os
import requests

from ..core.base_model import Model, ModelCapabilities
from ..core.errors import ApiKeyError, RequestError, RateLimitError

class OpenAICompatibleModel(Model):

    def __init__(self, 
            model_name: str|None = None, 
            max_async_calls:int = 7,
            additionnal_headers: Dict[str, Any] = {},
            api_parameters:Dict[str, Any] = {},
            capabilities:Set[ModelCapabilities] = {
                ModelCapabilities.TEXT2TEXT,
                ModelCapabilities.STREAMING,
            },
            base_url: str = "https://api.openai.com/v1", 
            chat_completion_url: str = "/chat/completions",
            embedding_url: str = "/embeddings",
            embedding_model_name: str|None = None,
            embedding_similarity_min: float = 0.30,  # Min similarity threshold for clustering
            api_key: str|None = None, 
            timeout: int = 300,
            retry_delay:int = 60,            
        ):     
        super().__init__(
            max_async_calls=max_async_calls,
            additionnal_headers=additionnal_headers,
            api_parameters=api_parameters,
            retry_delay=retry_delay
        )

        self.reasoning_start_and_stop_tags = ["<think>", "</think>"]
        self.model_name = model_name

        self.set_api_url(
            base_url, model_name, chat_completion_url,
            embedding_url, embedding_model_name, embedding_similarity_min
            )
        
        self.api_key = api_key
        self.timeout = timeout

        self.capabilities = capabilities

        self._used_tokens = 0
        self._nb_requests = 0

        if any(var is None for var in (model_name, base_url)):
            raise ValueError(f"[Model.__init__] Missing values.")
    
    def set_api_url(self, 
                    url: str, model_name: str, chat_completions_url: str,
                    embedding_url:str, embedding_model_name:str, embedding_similarity_min:float):
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
        else:
            hostname = url
            route = ""
        
        # Ollama/Vllm/Localhost overrides
        if hostname in ["127.0.0.1:11434", "localhost:11434"]:
            if route == "": route = "/api" # Default Ollama API prefix if not provided
        elif hostname in ["127.0.0.1:8000", "localhost:8000"]:
            if route == "": route = "/v1"
        if hostname and "openai.azure.com" in hostname:
            fix_azure_route = False
            if route == "":
                fix_azure_route = True
                route = "/openai/deployments/" + model_name
            if query == "":
                fix_azure_route = True
                query = "?api-version=2025-01-01-preview"

            if fix_azure_route:
                print(f"[OpenHosta] Fixing Azure route to: {schema}{hostname}{route}{route_extention}{query}")
       
        self.base_url = f"{schema}{hostname}"
        self.chat_completion_url = f"{route}{route_extention}{query}"
        
        # Prepend route prefix (e.g. /v1) to embedding_url, same as chat_completion_url
        if route and not embedding_url.startswith(route):
            embedding_url = route + embedding_url
        self.embedding_url = embedding_url if not self.base_url.endswith(embedding_url) else ""
        self.embedding_model_name = embedding_model_name or "text-embedding-3-small"
        self.embedding_similarity_min = embedding_similarity_min        
    
    def _get_api_key(self) -> str:
        # If key has not been set at application time, read it for each call
        api_key = self.api_key
        if api_key is None:
            api_key = os.environ.get("OPENHOSTA_DEFAULT_MODEL_API_KEY", None)
        return api_key

    def _get_headers(self, api_key: str) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        for key, value in self.additionnal_headers.items():
            headers[key] = value
        return headers

    def _generate_without_retry(self, messages: List[Dict[str, Any]], **kwargs) -> Dict:
        llm_args = kwargs
        if "force_json_output" in llm_args and ModelCapabilities.JSON_OUTPUT not in self.capabilities:
            llm_args.pop("force_json_output")

        api_key = self._get_api_key()
        if api_key is None and "api.openai.com/v1" in self.base_url:
            api_key = os.environ.get("OPENAI_API_KEY", None)
            if api_key is None:
                raise ApiKeyError("[OpenAICompatibleModel._generate_without_retry] Empty API key.")

        l_body = {
            "model": self.model_name,
            "messages": messages,
        }
        headers = self._get_headers(api_key)

        all_api_parameters = self.api_parameters | llm_args
        for key, value in all_api_parameters.items():
            if key == "force_json_output" and value:
                l_body["response_format"] = {"type": "json_object"}
            else:
                l_body[key] = value
        
        full_url = f"{self.base_url}{self.chat_completion_url}"
        response = requests.post(full_url, headers=headers, json=l_body, timeout=self.timeout)

        self._handle_rate_limit_headers(response)
            
        if response.status_code == 200:
            self._nb_requests += 1
            return response.json()
        elif response.status_code == 429:
            raise RateLimitError(f"[OpenAICompatibleModel._generate_without_retry] Rate limit exceeded. {response.text}")
        elif response.status_code == 401:
            raise ApiKeyError(f"[OpenAICompatibleModel._generate_without_retry] Unauthorized. {response.text}")
        else:
            raise RequestError(f"[OpenAICompatibleModel._generate_without_retry] Request failed ({response.status_code}):\n{response.text}")

    def _generate_stream_without_retry(self, messages: List[Dict[str, Any]], **kwargs):
        """Yield raw text delta chunks from the OpenAI-compatible SSE stream.
        
        Sends stream=True to the API and parses Server-Sent Events line by line.
        Each yielded value is a non-empty str delta (may be multi-token).
        """
        import json as _json

        llm_args = dict(kwargs)
        if "force_json_output" in llm_args and ModelCapabilities.JSON_OUTPUT not in self.capabilities:
            llm_args.pop("force_json_output")

        api_key = self._get_api_key()
        if api_key is None and "api.openai.com/v1" in self.base_url:
            api_key = os.environ.get("OPENAI_API_KEY", None)
            if api_key is None:
                raise ApiKeyError("[OpenAICompatibleModel._generate_stream_without_retry] Empty API key.")

        l_body: dict = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
        }
        headers = self._get_headers(api_key)

        all_api_parameters = self.api_parameters | llm_args
        for key, value in all_api_parameters.items():
            if key == "force_json_output" and value:
                l_body["response_format"] = {"type": "json_object"}
            elif key == "stream":
                pass  # already set
            else:
                l_body[key] = value

        full_url = f"{self.base_url}{self.chat_completion_url}"

        response = requests.post(
            full_url, headers=headers, json=l_body,
            timeout=self.timeout, stream=True
        )
        self._handle_rate_limit_headers(response)

        if response.status_code == 429:
            raise RateLimitError(f"[OpenAICompatibleModel._generate_stream_without_retry] Rate limit. {response.text}")
        if response.status_code == 401:
            raise ApiKeyError(f"[OpenAICompatibleModel._generate_stream_without_retry] Unauthorized. {response.text}")
        if response.status_code != 200:
            raise RequestError(f"[OpenAICompatibleModel._generate_stream_without_retry] Failed ({response.status_code}):\n{response.text}")

        self._nb_requests += 1
        for raw_line in response.iter_lines():
            if not raw_line:
                continue
            # SSE lines look like: "data: {...}" or "data: [DONE]"
            if isinstance(raw_line, bytes):
                raw_line = raw_line.decode("utf-8")
            if not raw_line.startswith("data:"):
                continue
            data_str = raw_line[len("data:"):].strip()
            if data_str == "[DONE]":
                break
            try:
                chunk = _json.loads(data_str)
            except _json.JSONDecodeError:
                continue
            delta = (
                chunk.get("choices", [{}])[0]
                     .get("delta", {})
                     .get("content") or ""
            )
            if delta:
                yield delta

    def _image_without_retry(self, prompt: str, **kwargs) -> Dict:
        api_key = self._get_api_key()
        headers = self._get_headers(api_key)
        
        l_body = {
            "model": self.model_name,
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "response_format": "url"
        }
        l_body.update(self.api_parameters)
        l_body.update(kwargs)
        
        full_url = f"{self.base_url}/images/generations"
        response = requests.post(full_url, headers=headers, json=l_body, timeout=self.timeout)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            raise RateLimitError(f"[OpenAICompatibleModel._image_without_retry] Rate limit exceeded. {response.text}")
        else:
            raise RequestError(f"[OpenAICompatibleModel._image_without_retry] Request failed ({response.status_code}): {response.text}")

    def _embed_without_retry(self, texts: List[str], **kwargs) -> List[List[float]]:
        api_key = self._get_api_key()
        headers = self._get_headers(api_key)
        
        body = {
            "model": self.embedding_model_name,
            "input": texts
        }
        body.update(kwargs)
        
        full_url = f"{self.base_url}{self.embedding_url}"
        
        try:
            response = requests.post(full_url, headers=headers, json=body, timeout=self.timeout)
            if response.status_code == 200:
                response_dict = response.json()
                embeddings = []
                data = response_dict.get("data", [])
                data_sorted = sorted(data, key=lambda x: x.get("index", 0))
                for item in data_sorted:
                    embeddings.append(item.get("embedding", []))
                return embeddings
            else:
                raise RequestError(f"[OpenAICompatibleModel._embed_without_retry] Request failed ({response.status_code}): {response.text}")
        except Exception as e:
            if isinstance(e, RequestError): raise e
            raise RequestError(f"[OpenAICompatibleModel._embed_without_retry] {str(e)}")

    def _handle_rate_limit_headers(self, response):
        if "Retry-After" in response.headers:
            self.set_next_rate_limit(next_authorized_api_call_time=response.headers["Retry-After"])
        elif 'x-ratelimit-reset-requests' in response.headers:
            self.set_next_rate_limit(next_authorized_api_call_time=response.headers['x-ratelimit-reset-requests'])
    
    def models_on_same_api(self) -> List[str]:
        api_key = self._get_api_key()
        if api_key is None and "api.openai.com/v1" in self.base_url:
            api_key = os.environ.get("OPENAI_API_KEY", None)
            if api_key is None:
                raise ApiKeyError("[OpenAICompatibleModel.models_on_same_api] Empty API key.")
        
        headers = self._get_headers(api_key)
        full_url = f"{self.base_url}/models"
        
        response = requests.get(full_url, headers=headers, timeout=self.timeout)
        if not response.ok:
            raise RequestError(f"[OpenAICompatibleModel.models_on_same_api] Request failed ({response.status_code}): {response.text}")
        
        model_list = []
        if "data" in response.json():
            for model in response.json()["data"]:
                if model.get("object") == "model":
                    model_list.append(model["id"])
        return model_list
    
    def get_consumption(self, response_dict) -> int:
        return self._used_tokens
    
    def get_response_content(self, response_dict: Dict) -> str:
        
        if "usage" in response_dict and "total_tokens" in response_dict["usage"]:
            self._used_tokens += int(response_dict["usage"]["total_tokens"])
    
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
        

    def print_last_prompt(self, inspection):
        """
        Print the last prompt sent to the LLM when using function `function_pointer`.
        """
        if "llm_api_messages_sent" in inspection.logs:
            for i, msg in enumerate(inspection.logs["llm_api_messages_sent"]):
                role = msg.get("role", "unknown")
                content = msg.get("content", [])
                
                text = ""
                if isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            text += part.get("text", "")
                        elif isinstance(part, str):
                            text += part
                elif isinstance(content, str):
                    text = content
                
                print(f"\n{role.capitalize()} prompt:\n-----------------")
                print(text)

        if "rational" in inspection.logs and inspection.logs["rational"]:
            print("\nRational:\n-----------------")
            print(inspection.logs["rational"])
        if "llm_api_response" in inspection.logs and \
            "choices" in inspection.logs["llm_api_response"] and \
                len(inspection.logs["llm_api_response"]["choices"]) >= 1:
            print("\nLLM response:\n-----------------")
            print(inspection.logs["llm_api_response"]["choices"][0]["message"].get("content", ""))

    # --- Removed old embedding_api_call as it's now handled by base class aliasing to _embed_without_retry ---
