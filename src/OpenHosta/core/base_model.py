from __future__ import annotations
from typing import Any, Dict, List, Set

import abc
import time 
import asyncio
from enum import Enum

from ..core.errors import RateLimitError

from  concurrent.futures import ThreadPoolExecutor

class ModelCapabilities(Enum):
    TEXT2TEXT = "TEXT2TEXT"
    TEXT2JSON = "TEXT2JSON"
    TEXT2IMAGE = "TEXT2IMAGE"
    IMAGE2TEXT = "IMAGE2TEXT"
    IMAGE2IMAGE = "IMAGE2IMAGE"
    LOGPROBS = "LOGPROBS" # To be set for vllm models
    
    THINK = "THINK"
    JSON_OUTPUT = "JSON_OUTPUT"

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
        
        # Rate limiting
        self.retry_delay = retry_delay
        self.delay_next_api_call_until = 0

    def __exit__(self):
        if self.async_executor is not None:
            self.async_executor.shutdown()
    
    def set_next_rate_limit(self, next_authorized_api_call_time:int):
        print(f"Set some delay before new API call. Waiting for {next_authorized_api_call_time}")
        self.delay_next_api_call_until = next_authorized_api_call_time + time.time()
    
    async def api_call_async(
        self,
        messages: List[dict[str, str]],
        llm_args:Dict = {}
    ) -> Dict:
        response_dict = await asyncio.get_event_loop().run_in_executor(
                self.get_executor(),
                self.api_call,
                messages, llm_args
            )
        return response_dict
    
    def get_executor(self):
        if self.async_executor is None:
            self.async_executor = ThreadPoolExecutor(max_workers=self.max_async_calls)
        return self.async_executor
    
    @abc.abstractmethod
    def models_on_same_api(self) -> List[str]:
        """
        List all models available on the same API.
        
        Returns:
            List[str]: List of model names.
        """
        raise NotImplementedError("You need to implement 'models_on_same_api' in your subclass of Model")
    
    def api_call(
        self,
        messages: List[Dict[str, str]],
        llm_args:Dict = {}
    ) -> Dict:
        now = time.time()
        
        time_to_wait = self.delay_next_api_call_until - now
        if time_to_wait > 0:
            print(f"Rate limit annouced. We wait for {time_to_wait}s before API call.")
            time.sleep(time_to_wait)
            
        try:
            # This is the api call to the model, nothing more. Easy to debug and test.
            response_dict = self.api_call_without_retry(messages, llm_args)
        except RateLimitError as e:
    
            if self.retry_delay == 0:
                raise e
            else:
                now = time.time()
                
                time_to_wait = self.delay_next_api_call_until - now                
                
                if time_to_wait <= 0:
                    # Delay other threads
                    print(f"Rate limit exceeded. But no delay was annouced by the API. We wait for {self.retry_delay}.")
                    self.delay_next_api_call_until = max(self.delay_next_api_call_until, now + self.retry_delay)
                
                # Delay this thread
                time_to_wait = self.delay_next_api_call_until - now
                if time_to_wait > 0:
                    print(f"Request failed due to rate limit exceeded. We wait for {time_to_wait}s then retry.", e)
                    time.sleep(time_to_wait)
                response_dict = self.api_call_without_retry(messages, llm_args) 
        
        return response_dict
    
    @abc.abstractmethod
    def  api_call_without_retry(
        self,
        messages: List[Dict[str, str]],
        llm_args:Dict = {}
    ) -> Dict:
        raise NotImplementedError("You need to implement 'api_call_without_retry' in your subclass of Model")

    @abc.abstractmethod
    def get_consumption(self, response_dict) -> int:
        """Return token consumption of the model for the given response_dict"""
        pass

    @abc.abstractmethod
    def get_response_content(self, response_dict: Dict) -> str:
        """Parse the response_dict and return the data section"""
        pass

