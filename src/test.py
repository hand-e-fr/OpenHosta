from pydantic import BaseModel

from OpenHosta.example import example
from OpenHosta.config import Model
from OpenHosta.emulate import emulate

mymodel = Model(
    model="gpt-4o",
    base_url="https://api.openai.com/v1/chat/completions",
    api_key=""
)

class User(BaseModel):
    name: str = None
    age: int = None
        
def user_info(template:User)->User:
    """
    This function fill the pydantic model in parameter with coherent values.
    """
    # example(a=10, b=3, hosta_out=30)
    # example(a=-1, b=-1, hosta_out=1)
    return emulate(model=mymodel)

res = user_info(User())
print(res)
print(type(res))
print(type(User()))
print(User(**res))



# import asyncio

# def is_animal(query:str)->bool:
#     """
#     Identifie si le mot est un animal
#     """
#     return emulate(model=mymodel)

# def is_country(query:str)->bool:
#     """
#     Identifie si le mot est un Pays
#     """
#     return emulate(model=mymodel)

# def is_color(query:str)->bool:
#     """
#     Identifie si le mot est une couleur
#     """
#     return emulate(model=mymodel)

# async def promesse(func, *args, **kwargs):
#     o = func(*args, **kwargs)
#     return o

# async def toto():
#     message = "Poule"
#     a = promesse(is_animal, message)
#     b = promesse(is_country, message)
#     c = promesse(is_color, message)
#     a, b, c = await asyncio.gather(a, b, c)
#     print(a, b, c)
    
# asyncio.run(toto())

