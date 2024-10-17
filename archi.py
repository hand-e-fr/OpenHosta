from __future__ import annotations

from typing import Callable, Tuple, Any, Optional, List, Union, Literal, Dict
from pydantic import BaseModel

from inspect import currentframe, unwrap
import inspect
from types import FrameType, CodeType
from copy import deepcopy

from OpenHosta.utils.errors import FrameError
from OpenHosta.core.analize import FuncAnalizer

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
        f_locals (dict): Local variables within the function's scope
    """
    f_def: str = ""
    f_name: str = ""
    f_call: str = ""
    f_args: Dict[str, Any] = {}
    f_type: Tuple[List[Any], Any] = ([], None)
    f_locals: Dict[str, Any] = {}

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
        self.exec:Callable = exec
        self.func:Callable = None
        self.caller_frame:FrameType = None

        self.infos = Func()

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
        analizer = FuncAnalizer(self.func, self.caller_frame)
        self.infos.f_name   = self.func.__name__
        self.infos.f_def, _ = analizer.func_def # car defintion + proto !
        self.infos.f_call   = analizer.func_call
        self.infos.f_args   = analizer.func_args
        self.infos.f_type   = analizer.func_type
        self.infos.f_locals = analizer.func_locals

# class HostaChecker(HostaInspector):
#     """
#     Post processing in the execution chain. 
#     Detect errors in the output to reduce uncertainty.
#     Manage all the typing process
#     """
#     def __init__(self):
#         """ Initialize the HostaInjector instance """
#         super().__init__()

#     def _type(self):
#         """ Checks output typing """
#         pass

