from __future__ import annotations

from typing import Tuple, List, Callable
from pydantic import BaseModel
import inspect

from .inspector import HostaInspector

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