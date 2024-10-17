from archi import HostaInspector
from typing import List,Literal, Union, Callable
from pydantic import BaseModel

class MemoryNode(BaseModel):
    """ All the data given by [example, thought, use] in the body of a function """
    key:Literal["ex", "cot", "use"]
    id:int
    value:Union[str, dict, Callable]

class HostaMemory(HostaInspector):
    """
    Handle all the data given in a body of a function and in the inspection,
    sort of a temporary cache.
    """
    
    def __init__(self, exec, attr_name):
        """ Initialize the HostaMemory instance """
        super().__init__()
        self._data:List[MemoryNode] = []
        self._last_added:MemoryNode = None
        self._func: Callable = None
        self._exec: Callable = exec
        self._attr_name: str = attr_name

    def __str__(self):
        """
        Manages a function's “_examples” and “_cothought” attributes,
        printing each type of element in a specific syntax
        """
        pass
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        """ Check for inconsistencies in the data order. """
        pass
        
    def add(self):
        """ Adds an element in the memory. """
        pass
        
    def get(self):
        """ Get all elements of a single type from memory. """
        pass

def set_hosta_path(path:str):
    """ Set the path for the '__hostacache__' directory by changing HOSTAPATH constant """
    pass

def save_example(func:Callable):
    """
    Extends the life of function examples by saving them in a file external to the program.
    """
    pass

        
