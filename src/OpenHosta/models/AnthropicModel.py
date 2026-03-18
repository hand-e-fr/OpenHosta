from __future__ import annotations
from typing import Any, Dict, List, Set, Tuple
import os
import requests
from ..core.base_model import Model, ModelCapabilities
from ..core.errors import ApiKeyError, RequestError, RateLimitError

class AnthropicModel(Model):
    def __init__(self, 
            model_name: str = "claude-3-5-sonnet-20240620", 
            max_async_calls = 7,
            additionnal_headers: Dict[str, Any] = {},
            api_parameters:Dict[str, Any] = {},
            capabilities:Set[ModelCapabilities] = {ModelCapabilities.TEXT2TEXT, ModelCapabilities.IMAGE2TEXT},
            base_url: str = "https://api.anthropic.com/v1",
            api_key: str = None, 
            timeout: int = 60,
            retry_delay:int = 60,            
        ):     
        super().__init__(
            max_async_calls=max_async_calls,
            additionnal_headers=additionnal_headers,
            api_parameters=api_parameters,
            retry_delay=retry_delay
        )
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.timeout = timeout
        self.capabilities = capabilities

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        headers.update(self.additionnal_headers)
        return headers

    def _generate_without_retry(self, messages: List[Dict[str, Any]], **kwargs) -> Dict:
        if not self.api_key:
            raise ApiKeyError("[AnthropicModel] Missing API key.")

        # Convert OpenAI-style messages to Anthropic style
        system_prompt = ""
        anthropic_messages = []
        for msg in messages:
            if msg["role"] == "system":
                # Anthropic takes system prompt as a top-level parameter
                content = msg["content"]
                if isinstance(content, list):
                    system_prompt += "\n".join([c.get("text", "") for c in content if c.get("type") == "text"])
                else:
                    system_prompt += str(content)
            else:
                # User/Assistant messages
                role = msg["role"]
                content = msg["content"]
                new_content = []
                if isinstance(content, str):
                    new_content.append({"type": "text", "text": content})
                elif isinstance(content, list):
                    for part in content:
                        if part.get("type") == "text":
                            new_content.append({"type": "text", "text": part.get("text", "")})
                        elif part.get("type") == "image_url":
                            # Anthropic expects: {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "..."}}
                            url = part.get("image_url", {}).get("url", "")
                            if "base64," in url:
                                media_type, data = url.split("base64,")
                                media_type = media_type.split(":")[1].split(";")[0]
                                new_content.append({
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": data
                                    }
                                })
                anthropic_messages.append({"role": role, "content": new_content})

        body = {
            "model": self.model_name,
            "messages": anthropic_messages,
            "max_tokens": kwargs.get("max_tokens", 4096)
        }
        if system_prompt:
            body["system"] = system_prompt
        
        # Merge other args
        for k, v in (self.api_parameters | kwargs).items():
            if k not in ["max_tokens", "force_json_output"]:
                body[k] = v

        response = requests.post(
            f"{self.base_url}/messages",
            headers=self._get_headers(),
            json=body,
            timeout=self.timeout
        )

        if response.status_code == 200:
            resp_json = response.json()
            # Map back to OpenAI-like format for internal consistency
            text = ""
            for block in resp_json.get("content", []):
                if block.get("type") == "text":
                    text += block.get("text", "")
            
            return {
                "choices": [{"message": {"content": text}}],
                "usage": {
                    "total_tokens": resp_json.get("usage", {}).get("input_tokens", 0) + resp_json.get("usage", {}).get("output_tokens", 0),
                    "prompt_tokens": resp_json.get("usage", {}).get("input_tokens", 0),
                    "completion_tokens": resp_json.get("usage", {}).get("output_tokens", 0)
                }
            }
        elif response.status_code == 429:
            raise RateLimitError(f"[AnthropicModel] Rate limit: {response.text}")
        else:
            raise RequestError(f"[AnthropicModel] Request failed ({response.status_code}): {response.text}")

    def _image_without_retry(self, prompt: str, **kwargs) -> Dict:
        raise NotImplementedError("Anthropic does not support text-to-image.")

    def _embed_without_retry(self, texts: List[str], **kwargs) -> List[List[float]]:
        # Anthropic doesn't have a public embedding API yet (they suggest using others)
        raise NotImplementedError("Anthropic does not support embeddings.")

    def get_consumption(self, response_dict: Dict) -> int:
        return response_dict.get("usage", {}).get("total_tokens", 0)

    def get_response_content(self, response_dict: Dict) -> str:
        return response_dict["choices"][0]["message"]["content"]
