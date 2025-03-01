# -*- coding: utf-8 -*-

# First install ollama
# then run ollama pull llama3.2:3b

import os

#########################################################
#
# Test model configuration
#
#########################################################

from OpenHosta import config

PORT=11434
#PORT=11436
MODEL_BASE_URL=os.environ.get("MODEL_BASE_URL", f"http://127.0.0.1:{PORT}/v1/chat/completions")
MODEL_API_KEY=os.environ.get("MODEL_API_KEY", "none")
MODEL_NAME = os.environ.get("MODEL_NAME", "DeepSeek-R1-huggingface")

model=config.Model(
    model="DeepSeek-R1-huggingface",
    json_output=False,
    timeout=120, # 2 minutes, reasoning models can be slow
    base_url=MODEL_BASE_URL,
    api_key="none",
    additionnal_headers={"Authorization":MODEL_API_KEY}
)

config.set_default_model(model)

#########################################################
#
# Test reasoning extraction
#
#########################################################

from OpenHosta import emulate

def capitalize_cities(sentence:str)->str:
    """
    This function capitalize the first letter of all city names in a sentence.
    Do not change other names. 

    Args:
       sentence (str): The sentence to process.
    """
    return emulate()

sentence = capitalize_cities("En juin paris hilton a ouvert son nouveau restaurant a londres.")

assert "Londres" in sentence

from OpenHosta import print_last_prompt, print_last_response

print_last_prompt(capitalize_cities)
print_last_response(capitalize_cities)
