from __future__ import annotations
from typing import Any, Dict, List, Set

import requests
import json
from .OpenAICompatible import OpenAICompatibleModel
from ..core.base_model import ModelCapabilities
from ..core.errors import ApiKeyError, RateLimitError, RequestError

class OllamaModel(OpenAICompatibleModel):
    """
    Model implementation for Ollama using its native API endpoints.
    Supported endpoints:
    - /api/generate for text generation
    - /api/embed for embeddings
    """

    def __init__(self, 
            model_name: str = None, 
            max_async_calls = 7,
            additionnal_headers: Dict[str, Any] = {},
            api_parameters:Dict[str, Any] = {},
            capabilities:Set[ModelCapabilities] = {ModelCapabilities.TEXT2TEXT, ModelCapabilities.JSON_OUTPUT},
            base_url: str = "http://localhost:11434", 
            generate_url: str = "/api/generate",
            embedding_url: str = "/api/embed",
            embedding_model_name: str = None,
            embedding_similarity_min: float = 0.30,
            api_key: str = None, 
            timeout: int = 60,
        ):     
        # We inherit from OpenAICompatibleModel but we will override the key methods
        super().__init__(
            model_name=model_name,
            max_async_calls=max_async_calls,
            additionnal_headers=additionnal_headers,
            api_parameters=api_parameters,
            capabilities=capabilities,
            base_url=base_url,
            embedding_model_name=embedding_model_name,
            embedding_similarity_min=embedding_similarity_min,
            api_key=api_key,
            timeout=timeout
        )
        self.embedding_model_name = embedding_model_name or model_name
        self.generate_url = generate_url
        self.embedding_url = embedding_url

    def api_call(
        self,
        messages: list[dict[str, Any]],
        llm_args: dict = {}
    ) -> Dict:
        """
        Call Ollama's native /api/generate endpoint.
        """
        if "force_json_output" in llm_args and ModelCapabilities.JSON_OUTPUT not in self.capabilities:
            llm_args.pop("force_json_output")

        # Convert messages to ollama format (prompt + images)
        # messages format is expected to be [{"role": "user", "content": [{"type": "text", "text": "..."}, {"type": "image_url", "image_url": {"url": "base64..."}}]}]
        prompts = []
        images = []
        
        for m in messages:
            if m.get("role") == "user":
                content = m.get("content", [])
                if isinstance(content, str):
                    prompts.append(content)
                elif isinstance(content, list):
                    for part in content:
                        if part.get("type") == "text":
                            prompts.append(part.get("text", ""))
                        elif part.get("type") == "image_url":
                            url = part.get("image_url", {}).get("url", "")
                            if "base64," in url:
                                images.append(url.split("base64,")[1])
                            else:
                                # Ollama expects raw base64 data
                                images.append(url)

        l_body = {
            "model": self.model_name,
            "prompt": "\n".join(prompts),
            "images": images,
            "stream": False
        }

        headers = {
            "Content-Type": "application/json"
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        for key, value in self.additionnal_headers.items():
            headers[key] = value

        all_api_parameters = self.api_parameters | llm_args
        for key, value in all_api_parameters.items():
            if key == "force_json_output" and value:
                l_body["format"] = "json"
            else:
                l_body[key] = value
        
        full_url = f"{self.base_url}{self.generate_url}"

        response = requests.post(full_url, headers=headers, json=l_body, timeout=self.timeout)

        if response.status_code == 200:
            pass
        elif response.status_code == 429:
            raise RateLimitError(f"[OllamaModel.api_call] Rate limit exceeded (HTTP 429). {response.text}")
        elif response.status_code == 401:
            raise ApiKeyError(f"[OllamaModel.api_call] Unauthorized (HTTP 401). Check your API key. {response.text}")
        else:
            raise RequestError(f"[OllamaModel.api_call] Request failed with status code {response.status_code}:\n{response.text}\n\n")
            
        self._nb_requests += 1

        # Ollama /api/generate returns a JSON or multiple JSONs if streaming (here stream=False)
        try:
            resp_json = response.json()
        except json.JSONDecodeError:
            # Fallback for multi-line JSON if something went wrong despite stream=False
            response_list = []
            for line in response.content.decode("utf-8").split("\n"):
                if line.strip():
                    response_list.append(json.loads(line))
            resp_json = response_list[-1]
            resp_json["response"] = "".join([l.get("response", "") for l in response_list])

        # Map Ollama response to internal format used by OpenHosta (OpenAI-like)
        response_content = resp_json.get("response", "")
        
        # Internal format expected: {"choices": [{"message": {"content": "..."}}]}
        response_dict = {
            "choices": [
                {
                    "message": {"content": response_content},
                    "logprobs": resp_json.get("logprobs", None)
                }
            ],
            "usage": {
                "total_tokens": resp_json.get("prompt_eval_count", 0) + resp_json.get("eval_count", 0),
                "prompt_tokens": resp_json.get("prompt_eval_count", 0),
                "completion_tokens": resp_json.get("eval_count", 0)
            }
        }
        
        return response_dict

    def embedding_api_call(self, texts: List[str]) -> List[List[float]]:
        """
        Call Ollama's native /api/embed endpoint.
        """
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        for key, value in self.additionnal_headers.items():
            headers[key] = value
            
        l_body = {
            "model": self.embedding_model_name or self.model_name,
            "input": texts
        }
        
        full_url = f"{self.base_url}{self.embedding_url}"
        
        try:
            response = requests.post(full_url, headers=headers, json=l_body, timeout=self.timeout)
            
            if response.status_code == 200:
                resp_json = response.json()
                # Ollama returns {"embeddings": [[...], [...]]}
                return resp_json.get("embeddings", [])
            else:
                # Log error and fallback
                return super().embedding_api_call(texts)
        except Exception:
            return super().embedding_api_call(texts)
