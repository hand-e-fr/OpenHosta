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
# pytest OpenHosta/tests/functionnalTests/test_emulate.py

from OpenHosta import emulate, config
from OpenHosta import print_last_prompt

config.DefaultModel.model_name = os.getenv("OPENHOSTA_MODEL_NAME", "gpt-4.1")
config.DefaultModel.base_url = os.getenv("OPENHOSTA_BASE_URL", "https://api.openai.com/v1")
config.DefaultModel.api_key = os.getenv("OPENHOSTA_OPENAI_API_KEY")

# Basic test to check if the emulate function works with a simple prompt
def test_emulate_basic():
    """
    Test the emulate function with a simple prompt that asks for the capital of a country.
    """
    def get_capital(country: str) -> str:
        """
        This function returns the capital of a given country.
        """
        return emulate()
    
    response = get_capital("France")
    assert "Paris" in response, f"Expected 'Paris' in response, got: {response}"


from  OpenHosta.core.hosta_inspector import get_caller_frame, get_hosta_inspection

def test_emulate_math():
    """
    Test the emulate function with a math operation.
    The interesting part of this test is to check if the type detection works.
    """
    def get_math_result(number: float) -> float:
        """
        Returns the result of the following math operation: 
        number + 2.
        
        Arguments:
            - number (float): A number to add to 2.
        Returns:
            - float: The result of the addition.
        """
        return emulate()
    response = get_math_result(2.5)
    assert 4.5 == response, f"Expected '4.5' in response, got: {response}"


    print_last_prompt(get_math_result)

from OpenHosta.pipelines import OneTurnConversationPipeline
def test_emulate_basic():
    """
    Test the emulate function with a simple prompt that asks for the capital of a country.
    """
    
    def get_capital(country: str) -> int:
        """
        This function returns the capital of a given country.
        """
        return emulate()
    
    response = get_capital("France")
    print_last_prompt(get_capital)
    
    assert response is None, f"Expected 'Paris' in response, got: {response}"

def test_emulate_routing():
    """
    Test the emulate function with a prompt that asks for the next step after a git command.
    """
    
    # define return type as enumeration
    from enum import StrEnum
    class NextStep(StrEnum):
        GIT_PUSH = "git push"
        GIT_COMMIT = "git commit"
        GIT_STATUS = "git status"
        GIT_PULL = "git pull"
        GIT_FETCH = "git fetch"
    
    def get_next_step(command: str) -> NextStep:
        """
        This function returns the next step after a git command.
        """
        return emulate()
    
    next_step = get_next_step("git commit -m 'Initial commit'")

    assert next_step is NextStep.GIT_PUSH, f"Expected 'git push' in response, got: {next_step}"
    
def test_emulate_dataclass():
    """
    Test the emulate function with a dataclass as return type.
    """
    from dataclasses import dataclass

    @dataclass
    class Person:
        name: str
        age: int

    def get_person_info(name: str) -> Person:
        """
        This function returns a Person object with the given name and a random age.
        """
        return emulate()
    
    person = get_person_info("Alice")
    
    assert isinstance(person, Person), f"Expected 'Person' in response, got: {type(person)}"
    