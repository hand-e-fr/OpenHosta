from typing import Any, Dict, List, Set
import os
from .OpenAICompatible import OpenAICompatibleModel
from ..core.base_model import ModelCapabilities

class HuggingFaceModel(OpenAICompatibleModel):
    """
    HuggingFace Inference API / Router implementation.
    HuggingFace provides an OpenAI-compatible endpoint.
    """
    def __init__(self, 
            model_name: str = "meta-llama/Llama-3.1-8B-Instruct", 
            max_async_calls = 7,
            additionnal_headers: Dict[str, Any] = {},
            api_parameters:Dict[str, Any] = {},
            capabilities:Set[ModelCapabilities] = {ModelCapabilities.TEXT2TEXT, ModelCapabilities.JSON_OUTPUT},
            base_url: str = "https://router.huggingface.co/v1", 
            api_key: str = None, 
            timeout: int = 60,
        ):     
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
