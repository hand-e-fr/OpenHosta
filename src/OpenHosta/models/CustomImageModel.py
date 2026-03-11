from __future__ import annotations
from typing import Any, Dict, List, Set, Tuple
import os
import requests
from ..core.base_model import Model, ModelCapabilities
from ..core.errors import RequestError

class CustomImageModel(Model):
    """
    Adapter for a custom image generator endpoint.
    Example: http://192.168.1.188:8000/generate
    """
    def __init__(self, 
            base_url: str = "http://192.168.1.188:8000/generate",
            max_async_calls = 2,
            additionnal_headers: Dict[str, Any] = {},
            api_parameters:Dict[str, Any] = {},
            capabilities:Set[ModelCapabilities] = {ModelCapabilities.TEXT2IMAGE},
            api_key: str = None, 
            timeout: int = 120,
        ):     
        super().__init__(
            max_async_calls=max_async_calls,
            additionnal_headers=additionnal_headers,
            api_parameters=api_parameters
        )
        self.model_name = "custom-image-gen"
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.capabilities = capabilities

    def _generate_without_retry(self, messages: List[Dict[str, Any]], **kwargs) -> Dict:
        raise NotImplementedError("CustomImageModel only supports image generation.")

    def _image_without_retry(self, prompt: str, **kwargs) -> Dict:
        body = {"prompt": prompt}
        body.update(self.api_parameters)
        body.update(kwargs)
        
        response = requests.post(
            self.base_url,
            headers=self.additionnal_headers,
            json=body,
            timeout=self.timeout
        )

        if response.status_code == 200:
            # Assuming it returns {"image_url": "..."} or {"b64_json": "..."}
            # We standardize to a simple dict
            return response.json()
        else:
            raise RequestError(f"[CustomImageModel] Failed: {response.text}")

    def _embed_without_retry(self, texts: List[str], **kwargs) -> List[List[float]]:
        raise NotImplementedError("CustomImageModel only supports image generation.")
