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

from OpenHosta import thinkof, thinkof_async

increment=thinkof("add one to this number")

assert increment(2) == 3

from OpenHosta import print_last_prompt, print_last_response

print_last_prompt(increment)
print_last_response(increment)

assert increment._return_type == int

rnd_flt=thinkof("return a random float")

assert type(rnd_flt("")) == float

hello_async=thinkof_async("say hello in a foreign language")
assert "onjour" in asyncio.run(hello_async("french"))
assert hello_async._return_type == str

from OpenHosta import emulate, emulate_async

def capitalize_cities(sentence:str)->str:
    """
    This function capitalize the first letter of all city names in a sentence.
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

print_last_prompt(capitalize_cities)
print_last_response(capitalize_cities)

from typing import Dict

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

sentence = "french president went with his wife brigite to london"
person_dict = find_people_dict(sentence)

assert all([k in sentence for k in person_dict.keys()])

print_last_prompt(find_people_dict)
print_last_response(find_people_dict)
