import os
from typing import Any

from ..core.base_model import ModelCapabilities
from .OpenAICompatible import OpenAICompatibleModel


class HuggingFaceModel(OpenAICompatibleModel):
    """
    HuggingFace Inference API / Router implementation.
    HuggingFace provides an OpenAI-compatible endpoint.
    """
    def __init__(self,
            model_name: str = "meta-llama/Llama-3.1-8B-Instruct",
            max_async_calls = 7,
            additionnal_headers: dict[str, Any] = None,
            api_parameters:dict[str, Any] = None,
            capabilities:set[ModelCapabilities] = None,
            base_url: str = "https://router.huggingface.co/v1",
            api_key: str = None,
            timeout: int = 60,
        ):
        if capabilities is None:
            capabilities = {ModelCapabilities.TEXT2TEXT, ModelCapabilities.JSON_OUTPUT}
        if api_parameters is None:
            api_parameters = {}
        if additionnal_headers is None:
            additionnal_headers = {}
        super().__init__(
            model_name=model_name,
            max_async_calls=max_async_calls,
            additionnal_headers=additionnal_headers,
            api_parameters=api_parameters,
            capabilities=capabilities,
            base_url=base_url,
            api_key=api_key or os.environ.get("HF_TOKEN"),
            timeout=timeout
        )
