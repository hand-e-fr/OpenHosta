from typing import Callable, Tuple, Any, Optional, List, Union, Literal
from pydantic import BaseModel

HOSTAPATH = "./"

class Func(BaseModel):
    """
    All the important about a function.
    Useful for the executive functions and the post-processing.
    """
    f_def:str
    f_call:str
    f_args:dict
    f_type:object

class HostaInspector:
    """
    This class is the parent class for a lot of OpenHosta functionnality.
    It provides methods which are used in many cases.
    """
    def __init__(self):
        """ Initialize the HostaInspector instance """
        pass
    
    def _extend(self)->Tuple[Callable, Any]:
        """
        Retrieves the object from the function in which it is called.
        """
        pass
    
    def _attach(self)->Optional[bool]:
        """
        Attach an attribute to a function or method .
        """
        pass
    
class HostaInjector(HostaInspector):
    """
    Takes a function as a parameter and injects the filled 'Func' pydantic
    as parameter.
    All instances of this class must therefore have the pydantic 'Func' 
    as the first parameter.
    """
    def __init__(self, exec:Callable):
        """ Initialize the HostaInjector instance """
        super().__init__()
        self.exec = exec
        
    def __call__(self, *args, **kwargs)->Func:
        """ 
        Make the instance callable. 
        Executes “self.exec”, providing the necessary information in a pydantic 'Func'.
        """
        infos:dict = {}
        return self.exec(infos, args, kwargs)

class HostaChecker(HostaInspector):
    """
    Post processing in the execution chain. 
    Detect errors in the output to reduce uncertainty.
    Manage all the typing process
    """
    def __init__(self):
        """ Initialize the HostaInjector instance """
        super().__init__()

    def _type(self):
        """ Checks output typing """
        pass

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
    
    def __init__(self):
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
    
    @_data.setter
    def _data(self, value):
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