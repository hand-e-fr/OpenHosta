import os
import time
import pytest
from dotenv import load_dotenv

load_dotenv()

from OpenHosta import emulate_iterator

# Force logprobs capability for testing
from OpenHosta import config
from OpenHosta.core.base_model import ModelCapabilities
config.DefaultModel.capabilities |= {ModelCapabilities.LOGPROBS}

# Basic test to check if the emulate function works with a simple prompt
def test_generate_basic():
    """
    This test checks if the emulate function works with a simple prompt in iterator mode.
    """
    from OpenHosta import print_last_prompt
    assistant_thinking_string = """Here is a random answer in asia """
    assistant_thinking_string = """<think>
    This time let's consider the answer that starts with '"""
    def country_name() -> str:
        """
        This function returns the name of a country.

        Returns:
            str: The name of a country.
        """
        return emulate_iterator(max_generation=10, assistant_thinking_string=assistant_thinking_string)

    it = country_name()
    next(it)
    for c in country_name():
        print(c)
        break
    print_last_prompt(country_name)

    def letters_of_the_alphabet() -> str:
        """
        This function returns a random letter of the alphabet.
        It should return only one character.

        Returns:
            str: The letter.
        """
        return emulate_iterator(max_generation=4, assistant_thinking_string=assistant_thinking_string)

    for c in letters_of_the_alphabet():
        print(c)
        break
        
    print_last_prompt(letters_of_the_alphabet)
    
    def get_city(country: str) -> str:
        """
        This function returns the capital of a given country.
        """
        return emulate_iterator(max_generation=5,assistant_thinking_string=assistant_thinking_string)

    for c in get_city("France"):
        print(c)
