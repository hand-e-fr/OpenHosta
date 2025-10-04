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
# Test sync and async functions
#
#########################################################

from OpenHosta import emulate

from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class Person(BaseModel):
    name: str = Field(..., description="The full name (Firstname and Sirname ) of the person")
    first_name: str = Field(..., description="The first name of the person")
    sir_name: str = Field(..., description="The sir name of the person")
    age: Optional[int] = None
    birth_city: Optional[str] = None

def find_people(sentence:str)->Person:
    """
    This function find people in a sentence.

    Identify the main person explicitly stated in the sentence.

    Return:
        A Person object.
    """
    return emulate()

first_person = find_people("The french president went with his wife Brigite Macron to london.")

from OpenHosta import print_last_prompt, print_last_decoding

print_last_prompt(find_people)
print_last_decoding(find_people)

assert "rigit" in first_person.name or "acron" in first_person.name or "resident" in first_person.name

# TODO: this is still ko. Il faut stacker les types lors du parcours recursif dans la structure
def find_people_list(sentence:str)->List[Person]:
    """
    This function find all people in a sentence.

    Identify all persons explicitly stated in the sentence.

    Return:
        A list of Person object.
    """
    return emulate()

person_list = find_people_list("french president went with his wife brigite to london")

print_last_prompt(find_people_list)
print_last_decoding(find_people_list)

assert any(["rigit" in person.name for person in person_list])

# TODO: this is still ko
def find_people_dict(sentence:str)->Dict[str, Person]:
    """
    This function find all people in a sentence.

    Identify all persons explicitly stated in the sentence.

    Return:
        A dictionary:
         key: the exact word or reference in sentence
         value: the Person object.
    """
    return emulate()

sentence = "french president went with his wife brigite to london"
person_dict = find_people_dict(sentence)

assert all([k in sentence for k in person_dict.keys()])

