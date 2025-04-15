from __future__ import annotations
from typing import Any, Dict

import os
import json
import requests

from ..models import DialogueModel
from ..utils.errors import ApiKeyError, RequestError

class OpenAICompatibleModel(DialogueModel):

    def __init__(self, 
            model_name: str = None, 
            max_async_calls = 7,
            additionnal_headers: Dict[str, Any] = {},
            api_parameters:Dict[str, Any] = {},
            json_output_capable:bool = True,
            base_url: str = None, 
            api_key: str = None, 
            timeout: int = 30,
        ):
        # DialogueModel.__init__(
        #     self,
        #     max_async_calls,
        #     additionnal_headers,
        #     api_parameters,
        #     json_output_capable,
        # )
                
        self.reasoning_start_and_stop_tags = ["<think>", "</think>"]
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key

        self.timeout = timeout

        self._used_tokens = 0
        self._nb_requests = 0

        if any(var is None for var in (model_name, base_url)):
            raise ValueError(f"[DialogueModel.__init__] Missing values.")
    
    def api_call(
        self,
        messages: list[dict[str, str]],
        force_json_output: bool = None,
        llm_args:dict = {}
    ) -> Dict:
        if force_json_output is None:
            force_json_output = self.json_output_capable

        api_key = self.api_key
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")

        if api_key is None and "api.openai.com/v1" in self.base_url:
            raise ApiKeyError("[model.api_call] Empty API key.")
        
        l_body = {
            "model": self.model_name,
            "messages": messages,
        }
        headers = {
            "Content-Type": "application/json"
        }
        
        if "azure.com" in self.base_url:
            headers["api-key"] = f"{api_key}"
        else:
            headers["Authorization"] = f"Bearer {api_key}"

        # for key, value in self.user_headers.items():
        #     headers[key] = value
 
        if force_json_output:
            l_body["response_format"] = {"type": "json_object"}
        for key, value in llm_args.items():
            l_body[key] = value
        try:
            response = requests.post(self.base_url, headers=headers, json=l_body, timeout=self.timeout)

            if response.status_code  != 200:
                response_text = response.text
                if "invalid_api_key" in response_text:
                    raise ApiKeyError("[DialogueModel.api_call] Incorrect API key.")
                else:
                    raise RequestError(
                        f"[DialogueModel.api_call] API call was unsuccessful.\n"
                        f"Status code: {response.status_code }:\n{response_text}"
                    )
            self._nb_requests += 1
            response_dict = response.json()
        
        except Exception as e:
            raise RequestError(f"[DialogueModel.api_call] Request failed:\n{e}\n\n")

        return response_dict
    
    
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

        if self.reasoning_start_and_stop_tags[0] in response and self.reasoning_start_and_stop_tags[1] in response:
            chunks = response[8:].split(self.reasoning_start_and_stop_tags[1])
            rational = chunks[0]
            answer = self.reasoning_start_and_stop_tags[1].join(chunks[1:]) # in case there are multiple </think> tags
        else:
            rational, answer = "", response
        
        return rational, answer
    

    def response_parser(self, response_dict: Dict) -> Any:

        if "usage" in response_dict:
            self._used_tokens += int(response_dict["usage"]["total_tokens"])

        response = response_dict["choices"][0]["message"]["content"]
        rational, answer = self.split_cot_answer(response)

        # if hasattr(function_metadata.f_obj, "_last_response") and \
        #     type(function_metadata.f_obj._last_response) is dict:
        #     function_metadata.f_obj._last_response["rational"] = rational
        #     function_metadata.f_obj._last_response["answer"] = answer
        response = self.extract_json(answer)
        
        try:
            if response.startswith("{"):
                l_ret_data = json.loads(response)
            else:
                l_ret_data = response
                
        except json.JSONDecodeError as e:
            # If not a JSON, use as is
            l_ret_data = response

        return l_ret_data

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
                # JSON not found in the response. (passthrough)"
                response = last_chunk
        
        return response
    