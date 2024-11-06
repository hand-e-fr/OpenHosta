from __future__ import annotations

from typing import Optional, Dict, Tuple, List, Any, get_args, get_origin
import inspect

from ..utils.import_handler import is_pydantic
from ..utils.hosta_type import MemoryNode

if is_pydantic:
    print("hello1")
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
        f_call: str = Field(default="", description="Actual call of the function, e.g., 'func(1, 'hello')'")
        f_args: Dict[str, Any] = Field(default_factory=dict, description="Arguments of the function, e.g., {'a': 1, 'b': 'hello'}")
        f_type: Tuple[List[Any], Any] = Field(default_factory=lambda: ([], None), description="Desired type of the input and output of the function")
        f_schema: Dict[str, Any] = Field(default_factory=dict, description="Dictionary describing the function's return type (in case of pydantic).")
        f_locals: Optional[Dict[str, Any]] = Field(default=None, description="Local variables within the function's scope")
        f_self: Optional[Dict[str, Any]] = Field(default=None)
        f_mem: Optional[List[MemoryNode]] = Field(default=None, description="Memory nodes associated with the function, contains examples, chain of thought...")
        
    def get_function_schema_pydantic(self) -> Dict[str, Any]:
        """
        Get the JSON schema of the function's return type.

        Returns:
            The JSON schema of the function's return type.
        """
        return_caller = self.sig.return_annotation if self.sig.return_annotation != inspect.Signature.empty else None
        return_schema = None

        if return_caller is not None:
            if get_origin(return_caller):
                return_caller_origin = get_origin(return_caller)
                return_caller_args = get_args(return_caller)
                combined = return_caller_origin[return_caller_args]
                new_model = create_model("return_schema", annotation=(combined, ...))
                return_schema = new_model.model_json_schema()
            elif issubclass(return_caller, BaseModel):
                return_schema = return_caller.model_json_schema()
            else:
                new_model = create_model("return_schema", annotation=(return_caller, ...))
                return_schema = new_model.model_json_schema()
        else:
            No_return_specified = create_model(
                "return_shema", annotation=(Any, ...)
            )
            return_schema = No_return_specified.model_json_schema()
        return return_schema  
else:
    print("hi1")
    class Func:
        f_obj: Optional[object] = None
        f_def: str = ""
        f_name: str = ""
        f_call: str = ""
        f_args: Dict[str, Any] = {}
        f_type: Tuple[List[Any], Any] = ([], None)
        f_schema: Dict[str, Any] = {}
        f_locals: Optional[Dict[str, Any]] = None
        f_self: Optional[Dict[str, Any]] = None
        f_mem: Optional[List[MemoryNode]] = None