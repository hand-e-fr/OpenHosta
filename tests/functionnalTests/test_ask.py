import os
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

from OpenHosta import ask, config

config.DefaultModel.model_name = os.getenv("OPENHOSTA_MODEL_NAME", "gpt-4.1")
config.DefaultModel.base_url = os.getenv("OPENHOSTA_BASE_URL", "https://api.openai.com/v1")
config.DefaultModel.api_key = os.getenv("OPENHOSTA_OPENAI_API_KEY")

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
