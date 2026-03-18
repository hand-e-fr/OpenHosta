from OpenHosta import config
from OpenHosta import ask,  emulate
from OpenHosta import MetaPrompt, OneTurnConversationPipeline, OpenAICompatibleModel

from OpenHosta.core.errors import ApiKeyError, RateLimitError, RequestError

from typing import Dict
import os
import requests

import json

class OllamaModel(OpenAICompatibleModel):

    def api_call(
        self,
        messages: list[dict[str, str]],
        llm_args:dict = {}
    ) -> Dict:

        if "force_json_output" in llm_args and ModelCapabilities.JSON_OUTPUT not in self.capabilities:
            llm_args.pop("force_json_output")

        api_key = self.api_key

        # Convert messages to ollama format


        prompts = [t['text'] for m in messages for t in m["content"] if m ["role"] == "user" and t["type"]  == "text"]
        images =  [t["image_url"]["url"] for m in messages for t in m["content"] if m ["role"] == "user" and t["type"]  == "image_url"]
        images = [i.split("base64,")[1] for i in images if "base64," in i]

        l_body = {
            "model": self.model_name,
            "prompt": "\n".join(prompts),
            "images": images,
            "stream": False
        }

        headers = {
            "Content-Type": "application/json"
        }

        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        for key, value in self.additionnal_headers.items():
            headers[key] = value

        all_api_parameters = self.api_parameters | llm_args
        for key, value in all_api_parameters.items():
            l_body[key] = value
        
        full_url = f"{self.base_url}/api/generate"

        response = requests.post(full_url, headers=headers, json=l_body, timeout=self.timeout)

        if response.status_code == 200:
            pass
        elif response.status_code == 429:
            raise RateLimitError(f"[Model.api_call] Rate limit exceeded (HTTP 429). {response.text}")
        elif response.status_code == 401:
            raise ApiKeyError(f"[Model.api_call] Unauthorized (HTTP 401). Check your API key. {response.text}")
        else:
            raise RequestError(f"[Model.api_call] Request failed with status code {response.status_code}:\n{response.text}\n\n")
            
        self._nb_requests += 1

        response_list = []
        for line in response.content.decode("utf-8").split("\n"):
            response_list.append(json.loads(line))

        response = ""
        for l in response_list:
            response += l["response"]

        response_dict = response_list[-1]        
        response_dict['list'] = response_list[:-1]
        response_dict["choices"] = [
            {
                "logprobs": {"content": response_list[-1]["logprobs"]},
                "message": {"content": response}
            }
            ]
        
        return response_dict    

from PIL import Image

from OpenHosta import safe
from OpenHosta.models import ModelCapabilities 

img = Image.open("HH_PAGE_1.png")

DeepSeekOCR = OpenAICompatibleModel(
    # model_name="qwen3-vl:4b-instruct",
    model_name="deepseek-ocr", 
    base_url="http://127.0.0.1:11434/v1")

DeepSeekOCR = OllamaModel(
    # model_name="qwen3-vl:4b-instruct",
    model_name="deepseek-ocr", 
    base_url="http://127.0.0.1:11434")


#DeepSeekOCR.capabilities |= { ModelCapabilities.LOGPROBS }

ocr_pipe = OneTurnConversationPipeline(
    model_list=[DeepSeekOCR],
    emulate_meta_prompt=MetaPrompt(""),
    user_call_meta_prompt=MetaPrompt("{{ function_doc }}"))

def get_markdown(img:Image.Image) -> str:
    """<image>
    <|grounding|>Convert the document to markdown."""
    return emulate(pipeline=ocr_pipe)


import time

max_size = 1280
factor = min(max_size/img.size[0], max_size/img.size[1])

new_size = [int(s*factor) for s in img.size]

img2 = img.resize(new_size)
#img2.show()
t0 = time.time()
with safe(acceptable_cumulated_uncertainty=1) as safe_context:
    out_md = get_markdown(img2)
    print(safe_context)
t1 = time.time()

print(f"Delata time: {t1-t0}")
# out_md = ask("<image>\n<|grounding|>Convert the document to markdown.", image=img)

print(out_md)

from OpenHosta import print_last_prompt
print_last_prompt(get_markdown)

boxes = [l for l in out_md.split("\n") if '<|det|>' in l]

box = eval('['+boxes[0].split("[[")[1].split(']]')[0]+']')

img2.crop(box).show()
