from typing import Any, Dict, List, Set, Optional
import os
import requests
import time
import io
from PIL import Image

from ..core.base_model import Model, ModelCapabilities
from ..core.errors import RequestError

class HuggingFaceReplicateModel(Model):
    """
    Implementation for HuggingFace Replicate Router (predictions API).
    Used for specific models like Qwen-Image that use the Replicate payload format.
    """
    def __init__(self, 
            model_name: str = "qwen/qwen-image-2512", 
            max_async_calls = 7,
            additionnal_headers: Dict[str, Any] = {},
            api_parameters:Dict[str, Any] = {},
            capabilities:Set[ModelCapabilities] = {
                ModelCapabilities.TEXT2TEXT, 
                ModelCapabilities.TEXT2IMAGE, 
                ModelCapabilities.IMAGE2TEXT,
                ModelCapabilities.IMAGE2IMAGE
            },
            base_url: str = "https://router.huggingface.co/replicate/v1/models", 
            api_key: str = None, 
            timeout: int = 120,
        ):     
        super().__init__(
            max_async_calls=max_async_calls,
            additionnal_headers=additionnal_headers,
            api_parameters=api_parameters,
        )
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key or os.environ.get("HH_INFERENCE_ENDPOINT") or os.environ.get("HF_TOKEN")
        self.timeout = timeout
        self.capabilities = capabilities

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "prefer": "wait"
        }
        headers.update(self.additionnal_headers)
        return headers

    def _generate_without_retry(self, messages: List[Dict[str, Any]], **kwargs) -> Dict:
        """
        Multimodal/Text generation using Replicate's prediction API.
        """
        prompt = ""
        images = []
        
        for m in messages:
            content = m.get("content", [])
            if isinstance(content, str):
                prompt += content + "\n"
            elif isinstance(content, list):
                for part in content:
                    if part.get("type") == "text":
                        prompt += part.get("text", "") + "\n"
                    elif part.get("type") == "image_url":
                        # Replicate usually takes image URLs or base64
                        url = part.get("image_url", {}).get("url", "")
                        images.append(url)

        # Replicate payload structure
        payload = {
            "input": {
                "prompt": prompt.strip()
            }
        }
        if images:
            # Depending on the model, it might take 'image' or 'images'
            # Qwen-Image often takes 'image' for single or specialized input
            payload["input"]["image"] = images[0] 
            if len(images) > 1:
                payload["input"]["images"] = images

        payload["input"].update(self.api_parameters)
        payload["input"].update(kwargs)

        prediction_url = f"{self.base_url}/{self.model_name}/predictions"
        headers = self._get_headers()
        
        response = requests.post(prediction_url, headers=headers, json=payload, timeout=self.timeout)
        if response.status_code not in [200, 201]:
            raise RequestError(f"HuggingFace Replicate API Error ({response.status_code}): {response.text}")

        resp_json = response.json()
        output = resp_json.get("output", "")
        
        # If output is a list (typical for Replicate), extract the first element
        if isinstance(output, list) and output:
            output = output[0]
            
        # Structure it back to look like a standard chat completion response for OpenHosta
        return {
            "choices": [
                {
                    "message": {"content": str(output)},
                    "finish_reason": "stop"
                }
            ],
            "usage": {"total_tokens": 0} # Replicate doesn't always provide this
        }

    def _image_without_retry(self, prompt: str, **kwargs) -> Dict:
        """
        Image generation using Replicate's prediction API.
        """
        payload = {
            "input": {
                "prompt": prompt
            }
        }
        payload["input"].update(self.api_parameters)
        payload["input"].update(kwargs)

        prediction_url = f"{self.base_url}/{self.model_name}/predictions"
        headers = self._get_headers()
        
        response = requests.post(prediction_url, headers=headers, json=payload, timeout=self.timeout)
        if response.status_code != 200:
            raise RequestError(f"HuggingFace Replicate API Error ({response.status_code}): {response.text}")

        resp_json = response.json()
        output = resp_json.get("output", [])
        
        if not output:
             raise RequestError(f"Empty output from Replicate: {resp_json}")

        img_url = output[0] if isinstance(output, list) else output
        
        # Download the image if requested or just return URL
        img_res = requests.get(img_url, headers={"Authorization": f"Bearer {self.api_key}"})
        img = Image.open(io.BytesIO(img_res.content))

        return {
            "created": int(time.time()),
            "data": [
                {
                    "url": img_url,
                    "image": img
                }
            ]
        }

    def _embed_without_retry(self, texts: List[str], **kwargs) -> List[List[float]]:
        raise NotImplementedError("Embeddings not supported for HuggingFace Replicate Router yet.")

    def get_consumption(self, response_dict) -> int:
        return 0

    def get_response_content(self, response_dict: Dict) -> str:
        return response_dict["choices"][0]["message"]["content"]
