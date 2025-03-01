from __future__ import annotations
from typing import Any, Dict

import json
import requests
import os
import re
import sys
import asyncio
from  concurrent.futures import ThreadPoolExecutor

from ..core.type_converter import TypeConverter
from ..utils.errors import ApiKeyError, RequestError
from ..core.hosta_inspector import FunctionMetadata


class Model:

    def __init__(self, 
            model: str = None, 
            base_url: str = None, 
            api_key: str = None, 
            timeout: int = 30,
            max_async_calls = 7,
            json_output:bool = True,
            additionnal_headers: Dict[str, Any] = {}
        ):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.max_async_calls = max_async_calls
        self.async_executor = None        
        self.user_headers = additionnal_headers
        self.json_output = json_output
        self._used_tokens = 0
        self._nb_requests = 0

        if any(var is None for var in (model, base_url)):
            raise ValueError(f"[Model.__init__] Missing values.")
        elif not is_valid_url(self.base_url):
            raise ValueError(f"[Model.__init__] Invalid URL.")
        
    def __exit__(self):
        if self.async_executor is not None:
            self.async_executor.shutdown()

    def get_executor(self):
        if self.async_executor is None:
            self.async_executor = ThreadPoolExecutor(max_workers=self.max_async_calls)
        return self.async_executor
        
    async def api_call_async(
        self,
        messages: list[dict[str, str]],
        json_output: bool = None,
        llm_args:dict = {}
    ) -> Dict:
        response_dict = await asyncio.get_event_loop().run_in_executor(
                self.get_executor(),
                self.api_call,
                messages, json_output, llm_args
            )
        return response_dict
    
    def api_call(
        self,
        messages: list[dict[str, str]],
        json_output: bool = None,
        llm_args:dict = {}
    ) -> Dict:
        if json_output is None:
            json_output = self.json_output

        if self.api_key is None and "api.openai.com/v1" in self.base_url:
            raise ApiKeyError("[model.api_call] Empty API key.")
        
        api_key = self.api_key
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")

        l_body = {
            "model": self.model,
            "messages": messages,
        }
        headers = {
            "Content-Type": "application/json"
        }
        
        if "azure.com" in self.base_url:
            headers["api-key"] = f"{api_key}"
        else:
            headers["Authorization"] = f"Bearer {api_key}"

        for key, value in self.user_headers.items():
            headers[key] = value
 
        if json_output:
            l_body["response_format"] = {"type": "json_object"}
        for key, value in llm_args.items():
            l_body[key] = value
        try:
            response = requests.post(self.base_url, headers=headers, json=l_body, timeout=self.timeout)

            if response.status_code  != 200:
                response_text = response.text
                if "invalid_api_key" in response_text:
                    raise ApiKeyError("[Model.api_call] Incorrect API key.")
                else:
                    raise RequestError(
                        f"[Model.api_call] API call was unsuccessful.\n"
                        f"Status code: {response.status_code }:\n{response_text}"
                    )
            self._nb_requests += 1
            response_dict = response.json()
        
        except Exception as e:
            raise RequestError(f"[Model.api_call] Request failed:\n{e}\n\n")

        return response_dict
    
    def response_parser(self, response_dict: Dict, function_metadata) -> Any:

        if "usage" in response_dict:
            self._used_tokens += int(response_dict["usage"]["total_tokens"])

        response = response_dict["choices"][0]["message"]["content"]
        rational, answer = self.split_cot_answer(response)

        if hasattr(function_metadata.f_obj, "_last_response") and \
            type(function_metadata.f_obj._last_response) is dict:
            function_metadata.f_obj._last_response["rational"] = rational
            function_metadata.f_obj._last_response["answer"] = answer
        
        response = self.extract_json(answer)
        
        try:
            l_ret_data = json.loads(response)['return']
        except json.JSONDecodeError as e:
            sys.stderr.write(
                f"[Model.response_parser] JSONDecodeError: {e}\nContinuing the process.")
            l_ret_data = ""

        return l_ret_data
    
    def type_returned_data(self, l_ret_data, function_metadata:FunctionMetadata):

        l_ret_data_typed = TypeConverter(function_metadata, l_ret_data).check()

        return l_ret_data_typed

    def split_cot_answer(self, response:str) -> tuple[str, str]:
        """
        This function split response into rational and answer.

        Special prompt may ask for chain-of-thought or models might be trained to reason first.

        Args:
            response (str): response from the model.

        Returns:
            tuple[str, str]: rational and answer.
        """
        response = response.strip()

        if response.startswith("<think>") and "</think>" in response:
            chunks = response[8:].split("</think>")
            rational = chunks[0]
            answer = "</think>".join(chunks[1:]) # in case there are multiple </think> tags
        else:
            rational, answer = "", response
        
        return rational, answer


    def extract_json(self, response: str) -> str:
        """
        Extracts the JSON part from the response.

        Some LLM will return the JSON with some additional text.
        """
        if response.strip().endswith("```"):
            chuncks = response.split("```")
            last_chunk = chuncks[-2]
            if "{" in last_chunk and "}" in last_chunk:
                chunk_lines = last_chunk.split("\n")[1:]
                # find first line with { and last line with }
                start_line = next(i for i, line in enumerate(chunk_lines) if "{" in line)
                end_line = len(chunk_lines) - next(i for i, line in enumerate(reversed(chunk_lines)) if "}" in line) - 1
                response = "\n".join(chunk_lines[start_line:end_line + 1])

            else:
                sys.stderr.write(
                    f"[Model.extract_json] JSON not found in the response. (passthrough)")
        
        return response


def is_valid_url(url: str) -> bool:
    regex = re.compile(
        r"^(?:http|ftp)s?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
        r"\[?[A-F0-9]*:[A-F0-9:]+\]?)"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return re.match(regex, url) is not None