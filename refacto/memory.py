from __future__ import annotations

from typing import Callable, Literal, List, Union
from pydantic import BaseModel

from .inspector import HostaInspector
from .injector import Func

# class MachinBuilder:
    
#     _batch_size = 0
#     _ziz_size = 0
    
#     def setBatchSize(self, value: int) -> MachinBuilder:
#         self._batch_size = value
#         return self
#     def setziziSize(self, value: int) -> MachinBuilder:
#         batch = value
#         return self
    
# MachinBuilder().setBatchSize(787)\
# .setziziSize(454)

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
    
    def __init__(self, func):
        """ Initialize the HostaMemory instance """
        super().__init__()
        self._data:List[MemoryNode] = []
        self._last_added:MemoryNode = None
        self._func:Func = None
        
    def __str__(self):
        """
        Manages a function's “_examples” and “_cothought” attributes,
        printing each type of element in a specific syntax
        """
        pass
     
    @property
    def data(self)->List[MemoryNode]:
        return self.data
    
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