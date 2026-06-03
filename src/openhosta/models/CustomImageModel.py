from __future__ import annotations

from typing import Any

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
            additionnal_headers: dict[str, Any] = None,
            api_parameters:dict[str, Any] = None,
            capabilities:set[ModelCapabilities] = None,
            api_key: str = None,
            timeout: int = 120,
        ):
        if capabilities is None:
            capabilities = {ModelCapabilities.TEXT2IMAGE}
        if api_parameters is None:
            api_parameters = {}
        if additionnal_headers is None:
            additionnal_headers = {}
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

    def _generate_without_retry(self, messages: list[dict[str, Any]], **kwargs) -> dict:
        raise NotImplementedError("CustomImageModel only supports image generation.")

    def _image_without_retry(self, prompt: str, **kwargs) -> dict:
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

    def _embed_without_retry(self, texts: list[str], **kwargs) -> list[list[float]]:
        raise NotImplementedError("CustomImageModel only supports image generation.")
