from __future__ import annotations

from typing import Optional, Dict, Any
from typing import get_args, get_origin

import json

from ..utils.import_handler import is_pydantic_available

if not is_pydantic_available:
    
    BaseModel = None

    # # Do not try to convert to pydantic object as the lib is not installed
    # def convert_pydantic(caller, checked):
    #     import sys
    #     sys.stdout.write("You shall install pydantic to use this function")
    #     return checked

    def get_pydantic_schema(return_caller) -> Optional[Dict[str, Any]]:
        """
        You shall install pydantic to use this function
        """
        return None

else:
    from pydantic import BaseModel

    def ispydanticclass(obj):
        try:
            l_ret = issubclass(obj, BaseModel)
        except Exception:
            l_ret = False
        return l_ret

    # def convert_pydantic(caller, checked) -> Optional[BaseModel]:
    #     """
    #     A method to convert the checked data based on the Pydantic model annotations of the function.

    #     Returns:
    #         Optional[BaseModel]: The converted checked data based on the Pydantic model annotations.
    #     """
    #             # Small models (SLM) tend to return well structired json as a string
    #     if type(checked) is str and ispydanticclass(caller):
    #         try:
    #             checked = json.loads(checked)
    #         except Exception as e:
    #             raise ValueError(f"LLM did not return a compatible structure for type `{caller}`:\n\t->{e} ")
        
    #     # Support for list of pydantic models
    #     if get_origin(caller) is list and ispydanticclass(get_args(caller)[0]):
    #         return [convert_pydantic(get_args(caller)[0], item) for item in checked]
    #     elif get_origin(caller) is dict and ispydanticclass(get_args(caller)[1]):
    #         return {get_args(caller)[0](k): convert_pydantic(get_args(caller)[1], v) for k, v in checked.items()}
    #     elif ispydanticclass(caller) and type(checked) is dict:
    #         return caller(**checked)
    #     else:
    #         # Unsuported type, keep as is
    #         return checked

    def get_pydantic_schema(return_caller) -> Optional[Dict[str, Any]]:
        """
        Get the JSON schema of the function's return type.

        Returns:
            The JSON schema of the function's return type.
        """

        if ispydanticclass(return_caller):
            return return_caller.model_json_schema()
        
        # Unsupported type
        return None

