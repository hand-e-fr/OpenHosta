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
    
    def country_name() -> str:
        """
        This function returns the name of a country near France, chosen randomly.

        Returns:
            str: The name of a country.
        """
        return emulate_iterator()


    for p in country_name():
        print(p)
        
    # This returns 19 names with qwen3-vl:8b-instruc (ollama)
    def country_name() -> str:
        """
        This function returns the name of a country, chosen randomly.

        Returns:
            str: The name of a country spelled in English.
        """
        return emulate_iterator(min_probability=1e-6, max_generation=100)

    def country_that_share_border_with(country: str) -> str:
        """
        This function returns the name of a country that shares a border with the given country, chosen randomly.
        
        Args:
           country (str): The name of the country.
        """
        return emulate_iterator()

    all = set()
    for p in country_name():
        all.add(p)
        print(f"\n{p}\n-----")
        for q in country_that_share_border_with(p):
            all.add(q)
            print(f"{p:20s} -> {q}")        
    
    len([x for x in all if len(x.split()) < 3])
    print([x for x in all if len(x.split()) < 3])
    
    def letters_of_the_alphabet() -> str:
        """
        This function returns a random letter of the alphabet.
        It should return only one character.

        Returns:
            str: The letter.
        """
        return emulate_iterator()

    for c in letters_of_the_alphabet():
        print(c)
            
    def get_city(country: str) -> str:
        """
        This function returns a city of that is in the country.
        The city is chosen randomly.
        
        Args:
           country (str): The name of the country.
        """
        return emulate_iterator()

    for country in country_name():
        for city in get_city(country):
            print(f"{country:20s}: {city}")


