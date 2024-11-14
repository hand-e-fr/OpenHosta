from __future__ import annotations

import inspect
from typing import Optional, Dict, Tuple, List, Any, get_args, get_origin

from ..utils.hosta_type import MemoryNode
from ..utils.import_handler import is_pydantic

if is_pydantic:
    from pydantic import BaseModel, Field, ConfigDict, create_model
    
    def convert_pydantic(caller, checked)->Optional[BaseModel]:
        """
        A method to convert the checked data based on the Pydantic model annotations of the function.

        Returns:
            Optional[BaseModel]: The converted checked data based on the Pydantic model annotations.
        """
        try:
            if issubclass(caller, BaseModel):
                return caller(**checked)
            return checked
        except:
            return checked

    class Func(BaseModel):
        """
        Func is a Pydantic model representing a function's metadata.
        Useful for the executive functions and the post-processing.
        """
        model_config = ConfigDict(arbitrary_types_allowed=True)
        f_obj: Optional[object] = Field(default=None)
        f_def: str = Field(default="", description="Simple definition of the function, e.g., 'def func(a:int, b:str)->int:'")
        f_name: str = Field(default="", description="Name of the function, e.g., 'func'")
        f_doc: str = Field(default="", description="Documentation of the function, e.g., 'This function returns the sum of two integers.'")
        f_call: str = Field(default="", description="Actual call of the function, e.g., 'func(1, 'hello')'")
        f_args: Dict[str, Any] = Field(default_factory=dict, description="Arguments of the function, e.g., {'a': 1, 'b': 'hello'}")
        f_type: Tuple[List[Any], Any] = Field(default_factory=lambda: ([], None), description="Desired type of the _inputs and _outputs of the function")
        f_schema: Dict[str, Any] = Field(default_factory=dict, description="Dictionary describing the function's return type (in case of pydantic).")
        f_sig: Optional[inspect.Signature] = Field(default=None, description="Signature of the function")
        f_locals: Optional[Dict[str, Any]] = Field(default=None, description="Local variables within the function's scope")
        f_self: Optional[Dict[str, Any]] = Field(default=None)
        f_mem: Optional[List[MemoryNode]] = Field(default=None, description="Memory nodes associated with the function, contains examples, chain of thought...")
        
    def get_pydantic_schema(return_caller) -> Optional[Dict[str, Any]]:
        """
        Get the JSON schema of the function's return type.

        Returns:
            The JSON schema of the function's return type.
        """
        try:
            if issubclass(return_caller, BaseModel):
                return return_caller.model_json_schema()
            return None
        except:
            return None

else:
    class Func:
        f_obj: Optional[object] = None
        f_def: str = ""
        f_name: str = ""
        f_doc: str = ""
        f_call: str = ""
        f_args: Dict[str, Any] = {}
        f_type: Tuple[List[Any], Any] = ([], None)
        f_schema: Dict[str, Any] = {}
        f_sig: Optional[inspect.Signature] = None
        f_locals: Optional[Dict[str, Any]] = None
        f_self: Optional[Dict[str, Any]] = None
        f_mem: Optional[List[MemoryNode]] = None