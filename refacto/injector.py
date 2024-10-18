from __future__ import annotations

from typing import Tuple, List, Callable, Dict, Any, Optional
from types import FrameType
from pydantic import BaseModel

from .inspector import HostaInspector
from .analize import FuncAnalizer
from .memory import HostaMemory

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
    f_locals: Optional[Dict[str, Any]] = None
      
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
        if not callable(exec):
            raise ValueError("[HostaInjector.__call__] Invalid argument. exec must be a callable.")
        self.exec:Callable = exec
        self.func:Callable = None
        self.caller_frame:FrameType = None
        self.infos = HostaMemory()

    def __call__(self, *args, **kwargs)->Func:
        """ 
        Make the instance callable. 
        Executes “self.exec”, providing the necessary information in a pydantic 'Func'.
        """
        self.func, self.caller_frame = self._extend()
        self.infos._func = self._get_infos_func()
        self._attach(self.func, {"_hostaInfos": self.serialize(self.infos)})
        return self.exec(self.infos, args, kwargs)
    
    def _get_infos_func(self) -> None:
        """
        parse a function to handle some infos
        """
        analizer = FuncAnalizer(self.func, self.caller_frame)
        self.infos.f_name   = self.func.__name__
        self.infos.f_def, _ = analizer.func_def
        self.infos.f_call   = analizer.func_call
        self.infos.f_args   = analizer.func_args
        self.infos.f_type   = analizer.func_type
        self.infos.f_locals = analizer.func_locals