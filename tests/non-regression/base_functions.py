# -*- coding: utf-8 -*-

# First install ollama
# then run ollama pull llama3.2:3b

import os
import asyncio

#########################################################
#
# Test model configuration
#
#########################################################

from OpenHosta import DefaultModel, ask

PORT=11434
MODEL_BASE_URL=os.environ.get("MODEL_BASE_URL", f"http://127.0.0.1:{PORT}/v1")
MODEL_API_KEY=os.environ.get("MODEL_API_KEY", "none")
MODEL_NAME = os.environ.get("MODEL_NAME", "qwen3:4b")

DefaultModel.model_name = MODEL_NAME
DefaultModel.base_url = MODEL_BASE_URL
DefaultModel.api_key = MODEL_API_KEY

from OpenHosta import closure, closure_async

increment=closure("add one to this number")

increment(29865.1)

ask("hello world!")


#########################################################
#
# Test sync and async functions
#
#########################################################

from OpenHosta import ask, ask_async

city = ask("what is the capital of France?")
assert "paris" in city.lower()

async def search():
    city1_co = ask_async("what is the capital of Poland?")
    city2_co = ask_async("what is the capital of USA?")
    city3_co = ask_async("what is the capital of France?")
    return await asyncio.gather(city1_co, city2_co, city3_co)

city1, city2, city3 = asyncio.run(search())    
assert "warsaw"     in city1.lower()
assert "washington" in city2.lower()
assert "paris"      in city3.lower()

from OpenHosta import closure, closure_async

increment=closure("add one to this number")

assert increment(2) == 3

from OpenHosta import print_last_prompt, print_last_response

print('Should print "No prompt found for this function."')
print_last_prompt(increment)
print_last_response(increment)

rnd_flt=closure("return a random float")

assert type(rnd_flt()) == float

hello_async=closure_async("say hello in a foreign language")
assert "onjour" in asyncio.run(hello_async("french"))

from OpenHosta import emulate, emulate_async

def capitalize_cities(sentence:str)->str:
    """
    This function capitalize the first letter of all city names in a sentence.
    Do it for cities you already know.
    """
    return emulate()

assert "Paris" in capitalize_cities("je suis allé à paris en juin")

async def capitalize_cities(sentence:str)->str:
    """
    This function capitalize the first letter of all city names in a sentence.
    """
    return await emulate_async()

sentence = asyncio.run(capitalize_cities("je suis allé à londres et los angeles en juin"))

assert "Londres" in sentence

print("Should print content")
print_last_prompt(capitalize_cities)
print_last_response(capitalize_cities)

from typing import Dict

# TODO: this is still ko
def find_people_dict(sentence:str)->Dict[str, int]:
    """
    This function find all people in a sentence and attach a short description of this person.

    Identify all persons explicitly stated in the sentence.

    Return:
        A dictionary:
         key:  exact word used to reference a person in the sentence
         value: the estimated age
    """
    return emulate()


def find_people_dict(sentence:str):
    """
    This function find all people in a sentence and attach a short description of this person.

    Identify all persons explicitly stated in the sentence.

    Return:
        A dictionary:
         key:  exact word used to reference a person in the sentence
         value: the estimated age
    """
    return emulate()

sentence = "french president went with his wife brigite to london"
person_dict = find_people_dict(sentence)

assert all([k in sentence for k in person_dict.keys()])

#print_last_prompt(find_people_dict)
#print_last_response(find_people_dict)
