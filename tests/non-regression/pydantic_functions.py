# -*- coding: utf-8 -*-

# First install ollama
# then run ollama pull llama3.2:3b

import os
import asyncio

from OpenHosta.utils.import_handler import is_pydantic_enabled
assert is_pydantic_enabled, "Pydantic shall be installed"

#########################################################
#
# Test model configuration
#
#########################################################

from OpenHosta import config

PORT=11434
PORT=11436
MODEL_BASE_URL=os.environ.get("MODEL_BASE_URL", f"http://127.0.0.1:{11436}/v1/chat/completions")
MODEL_API_KEY=os.environ.get("MODEL_API_KEY", "none")

#TODO: tester avec json_output = False
#TODO: tester models r1

model=config.Model(
    model="RTX3060-gemma2:9b",
    max_async_calls=10,
    base_url=MODEL_BASE_URL,
    timeout=120, api_key="none",
    additionnal_headers={"Authorization":MODEL_API_KEY}
)

config.set_default_model(model)

#########################################################
#
# Test sync and async functions
#
#########################################################

from OpenHosta import emulate, emulate_async

from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class Person(BaseModel):
    name: str = Field(..., description="The full name (Firstname and Sirname ) of the person")
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

fist_person = find_people("french president went with his wife brigite to london.")
from OpenHosta import print_last_prompt, print_last_response

print_last_prompt(find_people)
print_last_response(find_people)

assert "rigit" in fist_person.name or "acron" in fist_person.name or "resident" in fist_person.name

def find_people_list(sentence:str)->List[Person]:
    """
    This function find all people in a sentence.

    Identify all persons explicitly stated in the sentence.

    Return:
        A list of Person object.
    """
    return emulate()

person_list = find_people_list("french president went with his wife brigite to london")

assert any(["rigit" in person.name for person in person_list])

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

