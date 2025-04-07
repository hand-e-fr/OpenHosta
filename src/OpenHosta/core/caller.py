
from OpenHosta import DialogueModel



# Code -> LibOpenHosta -> Emulate -> DialogueModel
# Code -> Compiled
# Code -> Logger
#                         Emulate -> Logger
#                                    DialogueModel -> Logger

# use dagster



# TODO: test all combinations
# allow_thinking: T/F
# use_json_mode: T/F
# chain_of_thought: []
# examples_database: []

# Trois types de sortie LLM: string, json, python
# Map: 
# str -> string
# dataclass / pydantic -> json
# int, float, conplex, ...simple tupes... -> string + regexp
# callable -> python + regexp : test simple var definition + too call

# Input : python code, python repr, json, text
# Process: english string, python pseudo code 
# Output: string to regexp, string to json, string to regexp for python call plus data,  


# from pydantic import DialogueModel, Field
# class Toto(DialogueModel):
#     toto:str = Field(default="none", description="who is toto")


from OpenHosta.models import OpenAICompatible 

default_model = OpenAICompatible(
#        base_url="https://chat.hand-e.cloud/api/chat/completions",
        base_url="http://localhost:14434/v1/chat/completions",
#        model='mistral-small-2503',#'chatgpt-4o-latest',
        model='gemma3:1b',#'chatgpt-4o-latest',
        api_key="sk-2063d493d39544089c3fe31f90d9b468",
        json_output=False
        )

from typing import Dict


# Return types:
# - python: unsafe but better on small models
# - json: safe but slow and corrupted
# - raw: of for text only

### Exmaples


#### Example database

class Example:
    def __init__(self, **kwds):
        self.param=kwds
        self.values=[]
        self.is_unique = None
    
    def __eq__(self, value):
        self.value = value
        return self

    def returns(self, value):
        self.value = value
        return self

    def always_returns(self, value):
        if self.is_unique is False:
            raise Exception("You try to make unique a example that what already set as mutliple")
        self.is_unique = True
        self.values = [value]
        return self

    def may_returns(self, value):
        self.values.append(value)
        self.is_unique = False
        return self

    def __repr__(self):
        # This is supposed to be JSONL style, at least for basic types
        return '{' + f'"input": {self.param}, "output": {self.value}"' + '}\n'


### get_caller_function has to work with:
# - functions, 
# - objects methods, 
# - docorated function
# - decorated method
# - functions in functions, 
# - flask routed functions

# It returns:
# - the function pointer with its original name
# - the collable object that is used to reach this function (binder, wrapper, decorator, ...)

### function:
# - function pointer equals binder

from OpenHosta import emulate, predict

from OpenHosta import config

pipe_config = config.defaut_pipe.config
 
def find_country_of_town(town_name, zip=None, *, size, alt=0, population=None) -> str:
    """
    this function return the country of the town in parameter
    """
    return emulate(pipe_config=pipe_config)

frame = get_last_frame(find_country_of_town)

find_country_of_town(town_name="glasgow", size="1M")

# toto=find_country_of_town
# toto(45, "rdsd", dd=4)

### Object Method

class MyClass:
    Field1:int=3
    def methode_instance(self, b, arg, *, dd, fd=5, toto=44):
        return emulate()
    
    @staticmethod
    def staticmethod(b, arg, *, dd, fd=5, toto=44):
        return emulate()
    
    @classmethod
    def classmethod(cls, b, arg, *, dd, fd=5, toto=44):
        return emulate()
    
    def call_toto(self):
        return toto(45, "rdsd", dd=4)
    
    
mc = MyClass()
mc.methode_instance(45, "es", dd=5)
mc.staticmethod(45, "es", dd=5)
MyClass.staticmethod(45, "es", dd=5)
mc.classmethod(45, "es", dd=5)
MyClass.classmethod(45, "es", dd=5)

mc.call_toto()


### functions in functions

def foo(x=6):
    def foobar(val):
        return emulate()
    
    def bar(a=4):
        return foobar(a)
    return bar(x)

foo("f")

## Flask

from flask import Flask

app = Flask(__name__)

@app.route('/<page>')
def home(page=3)->str:
    return emulate()


if __name__ == '__main__':
    app.run(debug=True)



## Construct prompt

def my_function(b:int, arg:str, *, dd:int, fd:int=5, toto=44) -> Tuple:
    """
    This is my function that does simple things
    """
    remember_that(a=3, b='R').returns(4)
    return emulate()

frame = my_function(44, "rr", dd=4)
function_pointer = my_function

# my_function.hosta_inspection

# @dataclass
# class Personne:
#     nom: str
#     age: int
#     ville: str

# class PersonneN:
#     nom: str
#     age: int
#     ville: str
# # Création d'une instance de la classe
# personne0 = Personne(nom="Alice", age=30, ville="Paris")
# personne1 = Personne(nom="Alice", age=30, ville="Paris")

# personne2 = PersonneN()
# personne2.nom="Alice"
# personne2.age=30
# personne2.ville="Paris"
# personne2.__annotations__

# import json
# dataclass(MyClass).__annotations__
# MyClass.__annotations__

# personne0 == personne1
# personne1 == personne2


# # Affichage de l'objet
# print(personne1)

# personne1.__annotations__


