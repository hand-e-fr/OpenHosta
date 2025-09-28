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
# pytest OpenHosta/tests/functionnalTests/test_closure.py

from OpenHosta import closure, config


config.DefaultModel.model_name = os.getenv("OPENHOSTA_MODEL_NAME", "gpt-4.1")
config.DefaultModel.base_url = os.getenv("OPENHOSTA_BASE_URL", "https://api.openai.com/v1")
config.DefaultModel.api_key = os.getenv("OPENHOSTA_OPENAI_API_KEY")

# Basic test to check if the closure function works with a simple prompt
def test_closure_basic():
    get_capital = closure("What is the capital of this country?")
    response = get_capital("France")
    assert "Paris" in response, f"Expected 'Paris' in response, got: {response}"

def test_closure_math():
    get_math = closure("What is 2.0 + this number?")
    response = get_math(2.5)
    assert 4.5 == response, f"Expected '4.5' in response, got: {response}"

def test_closure_routing():
    prompt = "what is a good next step after this command: (between 'git push', 'git commit', 'git status', 'git pull', 'git fetch')"
    next_step = closure(prompt)
    response = next_step("git commit -m 'Initial commit'")
    assert "push" in response, f"Expected 'push' and 'origin' in response, got: {response}"
    
    
## Exact same tests but with async version of ask
from OpenHosta import closure_async
from asyncio import run

def test_closure_basic_async():
    async def app():
        get_capital = closure_async("What is the capital of this country?")
        return await get_capital("France")
    response = run(app())
    assert "Paris" in response, f"Expected 'Paris' in response, got: {response}"
    
def test_closure_math_async():
    async def app():
        get_math = closure_async("What is 2.0 + this number?")
        return await get_math(2.5)
    response = run(app())
    assert 4.5 == response, f"Expected '4.5' in response, got: {response}"
    
def test_closure_routing_async():
    async def app():
        prompt = "what is a good next step after this command: (between 'git push', 'git commit', 'git status', 'git pull', 'git fetch')"
        next_step = closure_async(prompt)
        return await next_step("git commit -m 'Initial commit'")
    response = run(app())
    assert "push" in response, f"Expected 'push' and 'origin' in response, got: {response}"
    
    