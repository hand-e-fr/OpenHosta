from typing import Callable, Tuple, Any, Optional, List, Union, Literal
from pydantic import BaseModel

from inspect import currentframe, unwrap
import inspect
from __future__ import annotations
from types import FrameType, CodeType
from copy import deepcopy

from OpenHosta.utils.errors import FrameError

HOSTAPATH = "./"

class Func(BaseModel):
    """
    Func is a Pydantic model representing a function's metadata.
    Useful for the executive functions and the post-processing.

    Attributes:
        f_def (str): Simple definition of the function, e.g., 'def func(a:int, b:str)->int:'
        f_name (str): Name of the function, e.g., 'func'
        f_call (str): Actual call of the function, e.g., 'func(1, 'salut')'
        f_args (dict): Arguments of the function, e.g., {'a': 1, 'b': 'salut'}
        f_type (object): desired type of the input and output of the function
    """
    f_def: str
    f_name: str
    f_call: str
    f_args: dict
    f_type: Tuple[List[object], object]
    f_locals:dict

class HostaInspector:
    """
    This class is the parent class for a lot of OpenHosta functionnality.
    It provides methods which are used in many cases.
    """
    def __init__(self):
        """ Initialize the HostaInspector instance """
        pass
    
    def _extend(self, *, back_level:int=2)->Tuple[Callable, FrameType]:
        """
        Retrieves the callable object and the frame from which this method is called.

        This method navigates up the call stack to find the function or method that called it.
        It can retrieve the callable object from both class methods and standalone functions.

        This method uses introspection to examine the call stack and local variables.
        It may not work correctly in all execution environments or with all types of callable objects.

        Args:
            - back_level (int, optional): The number of frames to go back in the call stack. 
                Defaults to 2. Must be a non-zero positive integer.

        Returns:
            Tuple[Callable, FrameType]: A tuple containing:
                - The callable object (function or method) that called this method.
                - The frame object of the caller.
        """
        assert back_level > 0 and isinstance(back_level, int),\
            f"ValueError: back_level param in _extend ({back_level})"
            
        def _get_obj_from_class(caller:FrameType)->Callable:
            """
            Search for the callable object when it is called within a class method.
            
            This function attempts to retrieve the method from the 'self' object
            in the caller's local variables. It's designed for internal use only, 
            within the _extend method.

            Args:
                caller (FrameType): The frame object of the calling method.

            Returns:
                Callable: The unwrapped method object if found, otherwise None.
            """
            func: Callable = None
            
            obj = caller.f_locals["self"]
            func = getattr(obj, caller_name, None)
            if func:
                func = unwrap(func)
            return func
        
        def _get_obj_from_func(caller:FrameType, code:CodeType, name:str)->Callable:
            """
            Search for the callable object when it is called within a function.
            
            This function traverses the call stack, examining local and global variables
            to find the function that matches the given code object. It's designed for
            internal use only, within the _extend method.
            
            Args:
                - caller (FrameType): The frame object of the calling function.
                - code (CodeType): The code object of the calling function.
                - name (str): The name of the calling function.

            Returns:
                Callable: The unwrapped function object if found, otherwise None.
            """
            func: Callable = None
            l_caller:FrameType = deepcopy(caller)
            
            while func is None and l_caller.f_back is not None:
                for obj in l_caller.f_back.f_locals.values():
                    found = False
                    try:
                        if hasattr(obj, "__code__"):
                            found = True
                    except:
                        continue
                    if found and obj.__code__ == caller_code:
                        func = obj
                        break
                if func is None:
                    l_caller = l_caller.f_back
            if func is None:
                func = caller.f_globals.get(caller_name)
                if func:
                    func = unwrap(func)
                    
        func: Callable = None
        current:FrameType = None
        
        current = currentframe()
        for k in range(back_level):
            current = current.f_back
            if current is None:
                raise FrameError(f"Frame can't be found (level: {k})")
            
        caller = current
        caller_name = caller.f_code.co_name
        caller_code = caller.f_code
        
        if "self" in caller.f_locals:
            _get_obj_from_class(caller)
        else:
            _get_obj_from_func(caller, caller_code, caller_name)
        
        if func is None or not callable(func):
            raise FrameError("The emulated function cannot be found.")

        return (func, caller)
    
    def _attach(self)->Optional[bool]:
        """
        Attach an attribute to a function or method .
        """
        pass

# module abc avec un héritage abstrait
class FuncAnalizer:
    
    def __init__(self, func: Callable):
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
        self.infos = Func()
        self.func = self._extend()

    def __call__(self, *args, **kwargs)->Func:
        """ 
        Make the instance callable. 
        Executes “self.exec”, providing the necessary information in a pydantic 'Func'.
        """
        self.infos = self._get_infos_func()
        return self.exec(self.infos, args, kwargs)
    
    def _get_infos_func(self) -> None:
        """
        parse a function to handle some infos
        """
        self.infos.f_def, _    = self.func_def() # car defintion + proto !
        self.infos.f_name   = self.func.__name__ # un truc comme ca a verifier meme enlever peut etre
        self.infos.f_call   = self.func_call()
        self.infos.f_args   = self.func_args()
        self.infos.f_type   = self.func_type()
        self.infos.f_locals = self.func_locals()
    

    # maybe put all of this func in another file for hosta injector clarity ?
    
    def func_def(self):
        """
        function that get the definition of his own func blablabal
        """
        if self.func == None or type(self.func) != Callable :
            raise ValueError("blablabla faire sa propre erreur")
        
        sig = inspect.signature(self.func)

        func_name = self.func.__name__
        func_params = ", ".join(
            [
                (
                    f"{param_name}: {param.annotation.__name__}"
                    if param.annotation != inspect.Parameter.empty
                    else param_name
                )
                for param_name, param in sig.parameters.items()
            ]
        )
        func_return = (
            f" -> {sig.return_annotation.__name__}"
            if sig.return_annotation != inspect.Signature.empty
            else ""
        )
        definition = (
            f"```python\ndef {func_name}({func_params}):{func_return}\n"
            f"    \"\"\"\n\t{self.func.__doc__}\n    \"\"\"\n```"
        )
        prototype = f"def {func_name}({func_params}):{func_return}"
        return definition, prototype # on fait def + proto mais est ce que on en ferait pas qu'un sur les deux (juste à rajouter func.doc pour la def c'est pour ça stp merlin dit oui !!!! (et jovilait aussi)) 
    def func_call(self):
        pass
    def func_args(self):
        pass
    def func_type(self):
        pass
    
    def func_locals(self):
        pass

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