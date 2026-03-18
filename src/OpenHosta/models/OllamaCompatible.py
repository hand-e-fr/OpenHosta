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
            timeout: int = 120,
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

        self.base_url = base_url.rstrip("/")
        self.generate_url = generate_url if generate_url.startswith("/") else "/" + generate_url
        self.embedding_url = embedding_url if embedding_url.startswith("/") else "/" + embedding_url
        self.embedding_model_name = embedding_model_name
        self.embedding_similarity_min = embedding_similarity_min

                

    def _generate_without_retry(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict:
        """
        Call Ollama's native /api/generate endpoint.
        """
        llm_args = kwargs
        if "force_json_output" in llm_args and ModelCapabilities.JSON_OUTPUT not in self.capabilities:
            llm_args.pop("force_json_output")

        # Convert messages to ollama format (prompt + images)
        prompts = []
        images = []
        
        for m in messages:
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
                            images.append(url)

        l_body = {
            "model": self.model_name,
            "prompt": "\n".join(prompts),
            "images": images,
            "stream": False
        }

        headers = self._get_headers(self.api_key or "")

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
            raise RateLimitError(f"[OllamaModel._generate_without_retry] Rate limit exceeded (HTTP 429). {response.text}")
        elif response.status_code == 401:
            raise ApiKeyError(f"[OllamaModel._generate_without_retry] Unauthorized (HTTP 401). {response.text}")
        else:
            raise RequestError(f"[OllamaModel._generate_without_retry] Request failed ({response.status_code}):\n{response.text}")
            
        self._nb_requests += 1

        try:
            resp_json = response.json()
        except json.JSONDecodeError:
            response_list = []
            for line in response.content.decode("utf-8").split("\n"):
                if line.strip():
                    response_list.append(json.loads(line))
            resp_json = response_list[-1]
            resp_json["response"] = "".join([l.get("response", "") for l in response_list])

        response_content = resp_json.get("response", "")
        
        response_dict = {
            "choices": [
                {
                    "message": {"content": response_content},
                    "logprobs": {"content": resp_json.get("logprobs", [])} if resp_json.get("logprobs") else None
                }
            ],
            "usage": {
                "total_tokens": resp_json.get("prompt_eval_count", 0) + resp_json.get("eval_count", 0),
                "prompt_tokens": resp_json.get("prompt_eval_count", 0),
                "completion_tokens": resp_json.get("eval_count", 0)
            }
        }
        
        return response_dict

    def _image_without_retry(self, prompt: str, **kwargs) -> Dict:
        """Ollama does not natively support text-to-image generation yet."""
        raise NotImplementedError("OllamaModel does not support image generation.")

    def _embed_without_retry(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Call Ollama's native /api/embed endpoint.
        NOTE: Sequential loop to avoid Ollama bug where batch inputs return identical vectors.
        """
        headers = self._get_headers(self.api_key or "")
        embeddings = []
        
        full_url = f"{self.base_url}{self.embedding_url}"
        
        for text in texts:
            l_body = {
                "model": self.embedding_model_name or self.model_name,
                "input": text  # Single string
            }
            l_body.update(kwargs)
            
            try:
                response = requests.post(full_url, headers=headers, json=l_body, timeout=self.timeout)
                if response.status_code == 200:
                    resp_json = response.json()
                    # In Ollama native API, if input is string, embeddings is list of 1 list
                    # or it might return "embedding": [...] directly?
                    # Let's check the response format for single input.
                    embs = resp_json.get("embeddings", [])
                    if embs:
                        embeddings.append(embs[0])
                else:
                    raise RequestError(f"[OllamaModel._embed_without_retry] Request failed ({response.status_code}): {response.text}")
            except Exception as e:
                if isinstance(e, RequestError): raise e
                raise RequestError(f"[OllamaModel._embed_without_retry] {str(e)}")
        
        return embeddings
