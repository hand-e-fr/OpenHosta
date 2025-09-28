# -*- coding: utf-8 -*-

#########################################################
#
# Test model configuration
#
#########################################################

import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# To run these tests you need to set .env variables to define an LLM provider
# e.g. for OpenAI:
# OPENHOSTA_LLM_PROVIDER=openai
# OPENHOSTA_OPENAI_API_KEY=your_api_key

# you also need to install pytest and python-dotenv:
# pip install pytest python-dotenv

# To run the tests, use the command:
# pytest OpenHosta/tests/functionnalTests/test_ask.py


from OpenHosta import config

config.DefaultModel.model_name = os.getenv("OPENHOSTA_MODEL_NAME", "gpt-4.1")
config.DefaultModel.base_url = os.getenv("OPENHOSTA_BASE_URL", "https://api.openai.com/v1")
config.DefaultModel.api_key = os.getenv("OPENHOSTA_OPENAI_API_KEY")

from OpenHosta.utils.import_handler import is_pydantic_available
assert is_pydantic_available, "Pydantic shall be installed"

#########################################################
#
# Test model configuration
#
#########################################################

from OpenHosta import ask
ask("hello world!")

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

from OpenHosta import print_last_prompt, print_last_decoding

print_last_prompt(capitalize_cities)
print_last_decoding(capitalize_cities)
