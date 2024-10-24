from typing import List
from pydantic import BaseModel, Field

import OpenHosta.core
from OpenHosta import config
from OpenHosta.emulate import emulate

config.set_default_apiKey("")

def multiply(a:int, b:int)->int:
    """
    This function multiplies two integers in parameter.
    """
    return emulate()

def random_list(size:int)->List[List[int]]:
    """
    This function returns a list of 4 list of random integers of the size in parameter.
    """
    return emulate()

class User(BaseModel):
    name:str = Field(description="The full name of the user.")
    age:int = Field(default=0, description="The age of the user. Default if older than 25.")
    mail:str = Field(description="The email of the user. Must end with \"gmail.com\".")
    friends:List[str] = Field(default_factory=list, description="A list of the user's friends first names.")

def fill_user_infos()->User:
    """
    This function fill the pydantic model with a randomly generated user.
    """
    return emulate()

res1 = multiply(5, 6)
print(res1)
print(type(res1))
print()

res2 = random_list(5)
print(res2)
print(type(res2))
print()

res3 = fill_user_infos()
print(res3)
print(type(res3))
print()