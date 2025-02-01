from __future__ import annotations

from typing import Optional, Dict, Any
from typing import get_args, get_origin

import json

from ..utils.import_handler import is_pydantic_enabled

if is_pydantic_enabled:
    from pydantic import BaseModel

    def convert_pydantic(caller, checked) -> Optional[BaseModel]:
        """
        A method to convert the checked data based on the Pydantic model annotations of the function.

        Returns:
            Optional[BaseModel]: The converted checked data based on the Pydantic model annotations.
        """
                # Small models (SLM) tend to return well structired json as a string
        if type(checked) is str and issubclass(caller, BaseModel):
            try:
                checked = json.loads(checked, )
            except Exception as e:
                raise ValueError(f"LLM did not return a compatible structure for type `{caller}`:\n\t->{e} ")
        
        # Support for list of pydantic models
        if get_origin(caller) is list and issubclass(get_args(caller)[0], BaseModel):
            return [convert_pydantic(get_args(caller)[0], item) for item in checked]
        elif get_origin(caller) is dict and issubclass(get_args(caller)[1], BaseModel):
            return {get_args(caller)[0](k): convert_pydantic(get_args(caller)[1], v) for k, v in checked.items()}
        elif issubclass(caller, BaseModel) and type(checked) is dict:
            return caller(**checked)
        else:
            # Unsuported type, keep as is
            return checked

    def get_pydantic_schema(return_caller) -> Optional[Dict[str, Any]]:
        """
        Get the JSON schema of the function's return type.

        Returns:
            The JSON schema of the function's return type.
        """
        if get_origin(return_caller) is list:
            return_caller = get_args(return_caller)[0]
        elif get_origin(return_caller) is dict:
            return_caller = get_args(return_caller)[1]
        
        if issubclass(return_caller, BaseModel):
            return return_caller.model_json_schema()
        
        # Unsupported type
        return None
else:

    # Do not try to convert to pydantic object as the lib is not installed
    def convert_pydantic(caller, checked):
        return checked

    def get_pydantic_schema(return_caller) -> Optional[Dict[str, Any]]:
        """
        You shall install pydantic to use this function
        """
        return None
