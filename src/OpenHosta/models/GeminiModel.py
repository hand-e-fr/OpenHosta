from __future__ import annotations
from typing import Any, Dict, List, Set, Tuple
import os
import requests
from ..core.base_model import Model, ModelCapabilities
from ..core.errors import ApiKeyError, RequestError, RateLimitError

class GeminiModel(Model):
    def __init__(self, 
            model_name: str = "gemini-1.5-flash", 
            max_async_calls = 7,
            additionnal_headers: Dict[str, Any] = {},
            api_parameters:Dict[str, Any] = {},
            capabilities:Set[ModelCapabilities] = {ModelCapabilities.TEXT2TEXT, ModelCapabilities.IMAGE2TEXT},
            base_url: str = "https://generativelanguage.googleapis.com/v1beta/models",
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
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.timeout = timeout
        self.capabilities = capabilities

    def _generate_without_retry(self, messages: List[Dict[str, Any]], **kwargs) -> Dict:
        if not self.api_key:
            raise ApiKeyError("[GeminiModel] Missing API key.")

        # Gemini format: {"contents": [{"role": "user", "parts": [{"text": "..."}]}]}
        gemini_contents = []
        system_instruction = None
        
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            if msg["role"] == "system":
                # Special handling for system instructions
                content = msg["content"]
                text = ""
                if isinstance(content, list):
                    text = "\n".join([c.get("text", "") for c in content if c.get("type") == "text"])
                else:
                    text = str(content)
                system_instruction = {"parts": [{"text": text}]}
                continue

            parts = []
            content = msg["content"]
            if isinstance(content, str):
                parts.append({"text": content})
            elif isinstance(content, list):
                for part in content:
                    if part.get("type") == "text":
                        parts.append({"text": part.get("text", "")})
                    elif part.get("type") == "image_url":
                        url = part.get("image_url", {}).get("url", "")
                        if "base64," in url:
                            media_type, data = url.split("base64,")
                            media_type = media_type.split(":")[1].split(";")[0]
                            parts.append({
                                "inline_data": {
                                    "mime_type": media_type,
                                    "data": data
                                }
                            })
            gemini_contents.append({"role": role, "parts": parts})

        body = {
            "contents": gemini_contents,
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 0.7),
            }
        }
        if system_instruction:
            body["system_instruction"] = system_instruction

        # Merge other args into generationConfig
        for k, v in (self.api_parameters | kwargs).items():
            if k not in ["max_tokens", "temperature", "force_json_output"]:
                body["generationConfig"][k] = v

        url = f"{self.base_url}/{self.model_name}:generateContent?key={self.api_key}"
        response = requests.post(url, json=body, timeout=self.timeout)

        if response.status_code == 200:
            resp_json = response.json()
            try:
                text = resp_json["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                text = ""
            
            return {
                "choices": [{"message": {"content": text}}],
                "usage": {
                    "total_tokens": resp_json.get("usageMetadata", {}).get("totalTokenCount", 0),
                    "prompt_tokens": resp_json.get("usageMetadata", {}).get("promptTokenCount", 0),
                    "completion_tokens": resp_json.get("usageMetadata", {}).get("candidatesTokenCount", 0)
                }
            }
        elif response.status_code == 429:
            raise RateLimitError(f"[GeminiModel] Rate limit: {response.text}")
        else:
            raise RequestError(f"[GeminiModel] Request failed ({response.status_code}): {response.text}")

    def _image_without_retry(self, prompt: str, **kwargs) -> Dict:
        # Google Imagen is separate, usually requires Vertex AI or different endpoint
        raise NotImplementedError("GeminiModel does not support direct image generation through this endpoint.")

    def _embed_without_retry(self, texts: List[str], **kwargs) -> List[List[float]]:
        if not self.api_key:
            raise ApiKeyError("[GeminiModel] Missing API key.")
        
        # Gemini embedding endpoint: models/{model}:embedContent
        # For multiple texts: models/{model}:batchEmbedContents
        
        full_url = f"{self.base_url}/text-embedding-004:batchEmbedContents?key={self.api_key}"
        
        requests_list = []
        for t in texts:
            requests_list.append({
                "model": "models/text-embedding-004",
                "content": {"parts": [{"text": t}]}
            })
            
        body = {"requests": requests_list}
        response = requests.post(full_url, json=body, timeout=self.timeout)
        
        if response.status_code == 200:
            embeddings = []
            for item in response.json().get("embeddings", []):
                embeddings.append(item.get("values", []))
            return embeddings
        else:
            raise RequestError(f"[GeminiModel.embed] Failed: {response.text}")

    def get_consumption(self, response_dict: Dict) -> int:
        return response_dict.get("usage", {}).get("total_tokens", 0)

    def get_response_content(self, response_dict: Dict) -> str:
        return response_dict["choices"][0]["message"]["content"]
