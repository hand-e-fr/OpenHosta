from OpenHosta import ask_stream, print_last_prompt

from OpenHosta import config

config.DefaultModel.api_parameters |= {"extra_body" : {"enable_thinking": False}, "reasoning_effort": "low"}

for line in ask_stream("liste les présidents de la france"):
    print("--->", line, end="", flush=True)
    
from typing import Iterator
from OpenHosta import emulate
from dataclasses import dataclass

@dataclass
class President:
    name: str
    start_date: str
    end_date: str

def list_all(what:str) -> Iterator[dict[str,str]]:
    """
    Iterate over all the items of a given type.
    :param what: The type of items to iterate over.
    :return: An iterator over the items of the given type.
    """
    return emulate()
    
for p in list_all("présidents de la france"):
    print(p)
    
print_last_prompt(list_all)