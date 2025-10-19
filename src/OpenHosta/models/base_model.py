from __future__ import annotations
from typing import Any, Dict

import abc
import asyncio
from enum import Enum

from  concurrent.futures import ThreadPoolExecutor

class ModelCapabilities(Enum):
    TEXT2TEXT = "TEXT2TEXT"
    TEXT2JSON = "TEXT2JSON"
    TEXT2IMAGE = "TEXT2IMAGE"
    IMAGE2TEXT = "IMAGE2TEXT"
    IMAGE2IMAGE = "IMAGE2IMAGE"
    
    THINK = "THINK"
    JSON_OUTPUT = "JSON_OUTPUT"

class Model:
    def __init__(self,
                max_async_calls = 7,
                additionnal_headers: Dict[str, Any] = {},
                api_parameters:Dict[str, Any] = {},
                ):
        self.capabilities: set[ModelCapabilities] = set()
        
        self.max_async_calls = max_async_calls
        self.async_executor = None
        
        self.additionnal_headers = additionnal_headers
        self.api_parameters = api_parameters
        
        self.preferred_image_format = "png"

    def __exit__(self):
        if self.async_executor is not None:
            self.async_executor.shutdown()
        
    async def api_call_async(
        self,
        messages: list[dict[str, str]],
        llm_args:dict = {}
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
    def  api_call(
        self,
        messages: list[dict[str, str]],
        llm_args:dict = {}
    ) -> Dict:
        raise NotImplementedError("You need to implement 'api_call' in your subclass of Model")

    @abc.abstractmethod
    def get_consumption(self, response_dict) -> int:
        """Return token consumption of the model for the given response_dict"""
        pass

    @abc.abstractmethod
    def get_response_content(self, response_dict: Dict) -> str:
        """Parse the response_dict and return the data section"""
        pass

