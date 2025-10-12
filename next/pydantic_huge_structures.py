### In version 3.0.0 of OpenHosta, we support simple Pydantic objects.
### This is a simple example of how to use it.
###
### The main limitations are:
### - we do not add Field descriptions to the prompt
### - we do not support nested models yet 

from pydantic import BaseModel, Field
from OpenHosta import emulate, print_last_decoding, print_last_prompt

class MyPydanticType(BaseModel):
    n: str = Field(..., description="the name of the user")
    g: str= Field(..., description="the gender of the user (Male or Female)")

def foo(bar:MyPydanticType, lang:str) -> str:
   """return Mr XXX or Mrs XXX in the selected language"""
   return emulate() 

foo(MyPydanticType(n="John", g="Male"), lang="fr")


print_last_prompt(foo)
print_last_decoding(foo)

from pydantic import BaseModel
from OpenHosta import emulate

class Person(BaseModel):
    name: str
    age: int

def find_first_name(sentence:str)->Person:
    """
    This function find in a text the name and the age of a person.

    Args:
        sentence: The text in which to search for information

    Return:
        A Pydantic model, but filled with the information. 
        If the information is not found, fill with the values with “None”.
    """
    return emulate()

find_first_name("My name is John and I am 30 years old")
# Person(name='John', age=30)