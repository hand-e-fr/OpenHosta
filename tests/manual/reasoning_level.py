import os
import time
import pytest
from dotenv import load_dotenv

load_dotenv()

from OpenHosta.models import OllamaModel, OpenAICompatibleModel
from OpenHosta import emulate, config

config.DefaultModel = OpenAICompatibleModel(
    model_name="qwen3.5:9b", 
    base_url="http://192.168.1.188:11434/v1",
    api_parameters={})

config.DefaultModel.api_call_without_retry([{"role": "user", "content": "Hello"}])


type LETTER=str

def first_letter_of(name: str) -> tuple[LETTER, LETTER]:
    """Returns the first letter and the last letter of the given name."""
    return emulate()

t0 = time.time()
response = first_letter_of("France")
t1 = time.time()
print(f"Time to get answer with low reasoning effort: {t1-t0:.2f} seconds")

from OpenHosta import print_last_prompt
print_last_prompt(first_letter_of)
