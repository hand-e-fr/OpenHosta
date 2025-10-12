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

