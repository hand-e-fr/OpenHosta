import os
import time
import pytest

from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

from OpenHosta import reload_dotenv
reload_dotenv()

from OpenHosta import emulate_variants

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

    from typing import Iterator
    @dataclass
    class Country:
        name: str

    def random_country_name() -> Iterator[Country]:
        """
        This function returns the name of a country near France.

        Returns:
            dict: The name of a country {"name": str}
        """
        return emulate_variants()


    for p in random_country_name():
        print(p)

    # print_last_prompt(random_country_name)

    # This returns 19 names with qwen3-vl:8b-instruc (ollama)
    def random_country_name() -> list[Country]:
        """
        This function returns the name of a country.

        Returns:
            dict: The name of a country {"name": str}
        """
        return emulate_variants(min_probability=1e-2, max_generation=100)

    def country_that_share_border_with(country: str) -> Iterator[Country]:
        """
        This function returns the name of a country that shares a border with the given country, chosen randomly.
        
        Args:
            dict: The name of a country {"name": str}
        """
        return emulate_variants(min_probability=1e-3)

    all = set()
    for p in random_country_name():
        all.add(p.name)
        print(f"\n{p}\n-----")
        for q in country_that_share_border_with(p.name):
            all.add(q.name)
            print(f"{p.name:20s} -> {q.name}")    
                
    len([x for x in all if len(x.split()) < 3])
    print([x for x in all if len(x.split()) < 3])

    def nicest_county_in_the_world() -> list[Country]:
        """
        This function returns the name of the nicest country in the world.
        
        Args:
            dict: The name of a country {"name": str}
        """
        return emulate_variants(min_probability=1e-3)

    list(nicest_county_in_the_world())
     
    def letters_of_the_alphabet() -> Iterator[str]:
        """
        This function returns a random letter of the alphabet.
        It should return only one character.

        Returns:
            str: The letter.
        """
        yield from emulate_variants()

    for c in letters_of_the_alphabet():
        print(c)
            
    def get_city(country: str) -> list[str]:
        """
        This function returns a city of that is in the country.
        The city is chosen randomly.
        
        Args:
           country (str): The name of the country.
        """
        return emulate_variants()

    for country in random_country_name():
        for city in get_city(country):
            print(f"{country:20s}: {city}")

    def dis_bonjour_avec_fautes(phrase:str) -> Iterator[str]:
        """
        Reformule la phrase avec les fautes d'orthograph les plus fréquentes.
        
        Args:
          phrase: La phrase à reformuler.
        
        Return:
          la même phrase avec des fautes d'orthographes.
        """
        return emulate_variants(min_probability=0.01)

    for c in dis_bonjour_avec_fautes("les chats font pas des chiens"):
        print(c)

    @dataclass
    class KG_LINK:
        link:str
        target:str    

    def add_grah_link(source) -> Iterator[KG_LINK]:
        """
        Suggest linkes in a knowledge graph.
        
        Args:
            source: The source node of the link.
        Return:
            KG_LINK: The link between the source and the target.
        """
        return emulate_variants(min_probability=0.001)
    
    for link in add_grah_link("friction"):
        print(link)