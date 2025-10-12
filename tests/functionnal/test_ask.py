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
# pytest OpenHosta/tests/functionnalTests/test_ask.py

from OpenHosta import ask

# Basic test to check if the ask function works with a simple prompt
def test_ask_basic():
    response = ask("What is the capital of France?")
    assert "Paris" in response, f"Expected 'Paris' in response, got: {response}"
    
def test_ask_math():
    response = ask("What is 2 + 2?")
    assert "4" in response, f"Expected '4' in response, got: {response}"
    
def test_ask_routing():
    prompt = "what git command is usually the next step after a git commit?"
    response = ask(prompt)
    assert "push" in response, f"Expected 'push' in response, got: {response}"
    
## Exact same tests but with async version of ask
from OpenHosta import ask_async
from asyncio import run

def test_ask_basic_async():
    async def app():
        return await ask_async("What is the capital of France?")
    response = run(app())
    assert "Paris" in response, f"Expected 'Paris' in response, got: {response}"

def test_ask_math_async():
    async def app():
        return await ask_async("What is 2 + 2?")
    response = run(app())
    assert "4" in response, f"Expected '4' in response, got: {response}"

def test_ask_routing_async():
    async def app():
        prompt = "what git command is usually the next step after a git commit?"
        return await ask_async(prompt)
    response = run(app())
    assert "push" in response, f"Expected 'push' in response, got: {response}"


def test_ask_speed():
    """
    Test the ask function with a very short prompt so that delay due to LLM is minimal.
    """

    t0 = time.time()
    for i in range(10):
        response = ask("Just answer with 1")
    t1 = time.time()
    
    print(f"10 calls to ask took {t1-t0:.2f} seconds, average {((t1-t0)/10):.2f} seconds per call")
    
    assert '1' in response, f"Expected '1' in response, got: {response}"
    assert (t1-t0) < 10, f"Expected less than 10 seconds for 10 calls, got: {t1-t0:.2f} seconds"
    