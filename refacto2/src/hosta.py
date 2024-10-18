from __future__ import annotations

from typing import Dict, Any, Tuple, List, Optional
from pydantic import BaseModel

from .inspector import HostaInspector
from .analizer import FuncAnalizer

all = (
    "Hosta"
)

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

class Hosta(HostaInspector):
    """
    Hosta is a class that extends HostaInspector and provides functionality for analyzing
    and storing information about the calling function.

    This class implements a singleton pattern and uses introspection to gather details
    about the callable that called the function that instantiated it.
    
    If many function instantiated it in the same callable, the first function will create
    an instance and attach it to the callable so that the next function can retrieve it.

    Attributes:
        _initialized (bool): Flag to track if the instance has been initialized.
        _obj (tuple): Stores the result of the _extend method call.
        _infos (Func): Stores detailed information about the analyzed function.
    """
    _initialized = False
    _obj = None
    
    def __new__(cls, *args, **kwargs)->'Hosta':
        """
        Create a new instance of Hosta or return the existing one if already created.

        This method implements the singleton pattern, ensuring only one instance of Hosta exists.
        It also handles the initialization of the instance when first created.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            > it's the arguments passed to __init__()

        Returns:
            Hosta: The single instance of the Hosta class.
        """
        cls._obj = cls._extend(back_level=3)
        if (hasattr(cls._obj[0], "Hosta")):
            return cls._obj[0].Hosta
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        setattr(cls._obj[0], "Hosta", instance)
        return instance
    
    def __init__(self, *, caller_analysis=True):
        """
        Initialize the Hosta instance.

        This method is called after __new__ and sets up the instance attributes.
        It also triggers the function analysis if caller_analysis is True.

        Args:
            caller_analysis (bool): If True, analyze the calling function. Defaults to True.
        """
        if not self._initialized:
            super().__init__()
            self._initialized = True
            self._infos = Func()
            if caller_analysis:
                self._get_infos_func()
            
    def _get_infos_func(self) -> None:
        """
        Analyze and store information about the calling function.

        This method uses FuncAnalizer to extract various details about the function
        that called the Hosta instance, including its name, definition, call signature,
        arguments, types, and local variables. This informations are useful in all OpenHosta's function.

        The extracted information is stored in the _infos attribute of the instance.
        """
        analizer = FuncAnalizer(self._obj[0], self._obj[1])
        self._infos.f_name   = self._obj[0].__name__
        self._infos.f_def, _ = analizer.func_def
        self._infos.f_call   = analizer.func_call
        self._infos.f_args   = analizer.func_args
        self._infos.f_type   = analizer.func_type
        self._infos.f_locals = analizer.func_locals
        
        
