from pydantic import BaseModel

from src.example import example
from src.config import Model
from src.emulate import emulate

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
