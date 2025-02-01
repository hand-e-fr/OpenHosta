from __future__ import annotations

from typing import Optional, Dict, Any

from ..utils.import_handler import is_pydantic_enabled

if is_pydantic_enabled:
    from pydantic import BaseModel

    def convert_pydantic(caller, checked) -> Optional[BaseModel]:
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
    # Do not try to convert to pydantic object as the lib is not installed
    def convert_pydantic(caller, checked):
        return checked

    def get_pydantic_schema(return_caller) -> Optional[Dict[str, Any]]:
        """
        You shall install pydantic to use this function
        """
        return None
