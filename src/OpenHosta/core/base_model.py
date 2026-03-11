from __future__ import annotations
from typing import Any, Dict, List, Set

import abc
import time 
import asyncio

from enum import Enum

from ..core.errors import RateLimitError

from  concurrent.futures import ThreadPoolExecutor

class ModelCapabilities(Enum):
    TEXT2TEXT = "TEXT2TEXT"      # Text input -> Text output
    TEXT2IMAGE = "TEXT2IMAGE"    # Text input -> Image output
    IMAGE2TEXT = "IMAGE2TEXT"    # (Text + Image) input -> Text output
    IMAGE2IMAGE = "IMAGE2IMAGE"  # (Text + Image) input -> Image output
    EMBEDDING = "EMBEDDING"      # Text input -> Vector output
    LOGPROBS = "LOGPROBS"        # API returns token probabilities
    THINK = "THINK"              # Model supports/emits reasoning tokens
    JSON_OUTPUT = "JSON_OUTPUT"  # API supports native JSON mode

class Model:
    def __init__(self,
                max_async_calls = 7,
                additionnal_headers: Dict[str, Any] = {},
                api_parameters:Dict[str, Any] = {},
                retry_delay:int = 60
                ):
        self.capabilities: Set[ModelCapabilities] = set()
        
        self.max_async_calls = max_async_calls
        self.async_executor = None
        
        self.additionnal_headers = additionnal_headers
        self.api_parameters = api_parameters
        
        self.preferred_image_format = "png"
        self.embedding_similarity_min = 0.30  # Default min similarity for clustering
        
        # Rate limiting
        self.retry_delay = retry_delay
        self.delay_next_api_call_until = 0

    def get_executor(self):
        if self.async_executor is None:
            self.async_executor = ThreadPoolExecutor(max_workers=self.max_async_calls)
        return self.async_executor

    def __exit__(self):
        if self.async_executor is not None:
            self.async_executor.shutdown()
    
    def set_next_rate_limit(self, next_authorized_api_call_time:str):
        if next_authorized_api_call_time.isdigit():
            next_authorized_api_call_time = int(next_authorized_api_call_time)
        elif next_authorized_api_call_time.endswith("s") and next_authorized_api_call_time[:-1].isdigit():
            next_authorized_api_call_time = int(next_authorized_api_call_time[:-1])
        elif next_authorized_api_call_time.endswith("ms"):
            next_authorized_api_call_time = int(next_authorized_api_call_time[:-2]) / 1000
        else:
            print(f"Invalid next_authorized_api_call_time: {next_authorized_api_call_time}. Seto to 0")
            next_authorized_api_call_time = 0
            
        print(f"Set some delay before new API call. Waiting for {next_authorized_api_call_time}")
        self.delay_next_api_call_until = next_authorized_api_call_time + time.time()
    
    async def generate_async(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict:
        """High-level async text generation."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self.get_executor(),
            lambda: self.generate(messages, **kwargs)
        )

    def generate(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict:
        """High-level text generation with retry logic."""
        return self._retry_wrapper(self._generate_without_retry, messages, **kwargs)

    def image(
        self,
        prompt: str,
        **kwargs
    ) -> Dict:
        """High-level image generation with retry logic."""
        return self._retry_wrapper(self._image_without_retry, prompt, **kwargs)

    def embed(
        self,
        texts: List[str],
        **kwargs
    ) -> List[List[float]]:
        """High-level embedding generation with retry logic."""
        return self._retry_wrapper(self._embed_without_retry, texts, **kwargs)

    def _retry_wrapper(self, func, *args, **kwargs):
        """Internal helper for rate-limit retries."""
        now = time.time()
        time_to_wait = self.delay_next_api_call_until - now
        if time_to_wait > 0:
            time.sleep(time_to_wait)

        try:
            return func(*args, **kwargs)
        except RateLimitError as e:
            if self.retry_delay == 0:
                raise e
            
            now = time.time()
            time_to_wait = self.delay_next_api_call_until - now
            if time_to_wait <= 0:
                self.delay_next_api_call_until = now + self.retry_delay
            
            time_to_wait = self.delay_next_api_call_until - now
            if time_to_wait > 0:
                time.sleep(time_to_wait)
            return func(*args, **kwargs)

    @abc.abstractmethod
    def _generate_without_retry(self, messages: List[Dict[str, Any]], **kwargs) -> Dict:
        pass

    @abc.abstractmethod
    def _image_without_retry(self, prompt: str, **kwargs) -> Dict:
        pass

    @abc.abstractmethod
    def _embed_without_retry(self, texts: List[str], **kwargs) -> List[List[float]]:
        pass

    # --- Backward Compatibility Alias ---
    def api_call(self, messages: List[Dict[str, str]], llm_args: Dict = {}) -> Dict:
        return self.generate(messages, **llm_args)

    async def api_call_async(self, messages: List[Dict[str, str]], llm_args: Dict = {}) -> Dict:
        return await self.generate_async(messages, **llm_args)

    def api_call_without_retry(self, messages: List[Dict[str, str]], llm_args: Dict = {}) -> Dict:
        return self._generate_without_retry(messages, **llm_args)

    def embedding_api_call(self, texts: List[str]) -> List[List[float]]:
        return self.embed(texts)

    @abc.abstractmethod
    def get_consumption(self, response_dict) -> int:
        """Return token consumption of the model for the given response_dict"""
        pass

    @abc.abstractmethod
    def get_response_content(self, response_dict: Dict) -> str:
        """Parse the response_dict and return the data section"""
        pass