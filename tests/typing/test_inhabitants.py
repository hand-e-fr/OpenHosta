from dataclasses import dataclass
from OpenHosta import emulate

@dataclass
class Person:
    name:str
    yearofbirth:int
    yearofdeath:int|None
    link_type:str
    occupation:str
    
def list_knwon_inhabitants(country:str, town:str) -> list[Person]:
    """
    List the main public personalities associated to the town.
    The association can be by birth, death, main working place or residence.
    :param country: The country where the town is located
    :param town: The town to list the inhabitants of
    """
    return emulate()

if __name__ == '__main__':
    res = list_knwon_inhabitants("France", "Saint-Etienne")
    print(res)
