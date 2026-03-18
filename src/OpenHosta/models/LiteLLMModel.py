from typing import Any, Dict, List, Set, Tuple, Optional
import os
import yaml
import litellm
from litellm import Router
from .OpenAICompatible import OpenAICompatibleModel
from ..core.base_model import Model, ModelCapabilities
from ..core.errors import RequestError, ApiKeyError, RateLimitError

class LiteLLMModel(Model):
    """
    Model implementation using the LiteLLM Python library directly.
    Supports almost all providers via a unified interface.
    """
    def __init__(self, 
            model_name: str, 
            config_path: Optional[str] = None,
            max_async_calls = 7,
            additionnal_headers: Dict[str, Any] = {},
            api_parameters:Dict[str, Any] = {},
            capabilities:Set[ModelCapabilities] = {ModelCapabilities.TEXT2TEXT, ModelCapabilities.JSON_OUTPUT},
            api_key: Optional[str] = None, 
            timeout: int = 60,
        ):     
        super().__init__(
            max_async_calls=max_async_calls,
            additionnal_headers=additionnal_headers,
            api_parameters=api_parameters
        )
        self.model_name = model_name
        self.api_key = api_key
        self.timeout = timeout
        self.capabilities = capabilities
        self.router = None
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                model_list = config.get("model_list", [])
                self.router = Router(model_list=model_list)

    def _generate_without_retry(self, messages: List[Dict[str, Any]], **kwargs) -> Dict:
        llm_args = self.api_parameters | kwargs
        
        # litellm expects OpenAI format messages
        try:
            if self.router:
                response = self.router.completion(
                    model=self.model_name,
                    messages=messages,
                    **llm_args
                )
            else:
                response = litellm.completion(
                    model=self.model_name,
                    messages=messages,
                    api_key=self.api_key,
                    **llm_args
                )
            
            # litellm returns a ModelResponse object that behaves like a dict
            return response.json() if hasattr(response, "json") else dict(response)
        
        except litellm.exceptions.RateLimitError as e:
            raise RateLimitError(str(e))
        except litellm.exceptions.AuthenticationError as e:
            raise ApiKeyError(str(e))
        except Exception as e:
            raise RequestError(str(e))

    def _image_without_retry(self, prompt: str, **kwargs) -> Dict:
        llm_args = self.api_parameters | kwargs
        try:
            response = litellm.image_generation(
                model=self.model_name,
                prompt=prompt,
                api_key=self.api_key,
                **llm_args
            )
            return response.json() if hasattr(response, "json") else dict(response)
        except Exception as e:
            raise RequestError(str(e))

    def _embed_without_retry(self, texts: List[str], **kwargs) -> List[List[float]]:
        llm_args = self.api_parameters | kwargs
        try:
            response = litellm.embedding(
                model=self.model_name,
                input=texts,
                api_key=self.api_key,
                **llm_args
            )
            # Standard OpenAI-like layout: {"data": [{"embedding": [...]}, ...]}
            embeddings = []
            for item in response.get("data", []):
                embeddings.append(item.get("embedding", []))
            return embeddings
        except Exception as e:
            raise RequestError(str(e))

    def get_consumption(self, response_dict: Dict) -> int:
        return response_dict.get("usage", {}).get("total_tokens", 0)

    def get_response_content(self, response_dict: Dict) -> str:
        return response_dict["choices"][0]["message"]["content"]
