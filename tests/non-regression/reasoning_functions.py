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
PORT=11436
MODEL_BASE_URL=os.environ.get("MODEL_BASE_URL", f"http://127.0.0.1:{11436}/v1/chat/completions")
MODEL_API_KEY=os.environ.get("MODEL_API_KEY", "none")

deepseek_r1_14b_rtx3060 = config.Model(
        base_url=MODEL_BASE_URL,
        model="deepseek-r1:14b",
        timeout=120, # 2 minutes, reasoning models can be slow
        json_output=False, # For reasoning models, json_output shall be False as there is a first part that is non JSON
        api_key="none",
        additionnal_headers={"Authorization":"Basic ZWJhdHQ6UFM3cno0QTdja1VpTEt3VlNYa2VDTURZVnFXMHZ4cUw="}
        )

config.set_default_model(deepseek_r1_14b_rtx3060)

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
