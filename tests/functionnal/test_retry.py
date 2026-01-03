import os
import time
import pytest
from dotenv import load_dotenv

load_dotenv()

# To run these tests you need to set .env variables to define an LLM provider
# e.g. for OpenAI:
# OPENHOSTA_LLM_PROVIDER=openai
# OPENHOSTA_OPENAI_API_KEY=your_api_key

# you also need to install pytest and python-dotenv:
# pip install pytest python-dotenv

# To run the tests, use the command:
# pytest OpenHosta/tests/functionnalTests/test_emulate.py

from OpenHosta import emulate, emulate_async

import asyncio

def test_emulate_loop():
    """
    Test the emulate function with a simple prompt with loop.
    """
    
    def get_capital_name(country: str) -> str:
        """
        This function returns the name of the capital of a given country.
        """
        return emulate()
    
    try:
        for _ in range(50):
            response = get_capital_name("France")
            print(response)
    except Exception as e:
        print(e)
        response = None
                
    assert response == "Paris", "The response should be 'Paris'."
    
# Basic test to check if the emulate function works with a simple prompt
def test_emulate_parallel():
    """
    Test the emulate function with a simple prompt with as many call as possible un parallel.
    """
    
    async def get_capital_name(country: str) -> str:
        """
        This function returns the name of the capital of a given country.
        """
        return await emulate_async()
    
    async def get_all(parallel_calls):
        call_list = [get_capital_name("France") for _ in range(parallel_calls)]
        return await asyncio.gather(*call_list)

    call_count = 50
    responses = asyncio.run(get_all(call_count))
    assert len(responses) == call_count, "The number of responses should be equal to the number of parallel calls."
    assert all([response == "Paris" for response in responses]), "All responses should be 'Paris'."


