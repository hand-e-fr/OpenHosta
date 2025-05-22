from __future__ import annotations

import inspect
import json
import textwrap
from typing import _alias
from dataclasses import is_dataclass

import sys
from sys import version_info
from typing import Type, Any, Callable, TypeVar, get_origin

from .pydantic_stub import convert_pydantic

T = TypeVar('T')

if version_info.major == 3 and version_info.minor > 9:
    from types import NoneType
else:
    NoneType = type(None)

def type_returned_data(untyped_response: str, expected_type: Type[T]) -> T:
    """
    Convert the untyped response to the expected type.
    """
    
    # In a real implementation, you might want to use a more sophisticated approach
    return convert_pydantic(json.loads(untyped_response), expected_type)

BASIC_TYPES = [
    int, float, complex, str, list, tuple, range, dict, set, frozenset,
    bool, bytes, bytearray, memoryview
]


def describe_type_as_schema(arg_type):
    """
    Describe a Python type as a JSON schema.
    """
    return None

def describe_type_as_python(arg_type):
    type_definition = None
    
    if arg_type in BASIC_TYPES or\
        type(arg_type) is _alias or\
            arg_type == type:
        # Check if the type is a basic type or a typing alias
        type_definition = nice_type_name(arg_type)

    elif is_dataclass(arg_type):
        type_definition=textwrap.dedent(f"""\
            python class {arg_type.__name__} is defines as a @dataclass:
            {arg_type.__doc__}
            """)
        
    elif hasattr(arg_type, '__annotations__')  and \
            not arg_type.__annotations__ is inspect._empty:
        # This is a class with annotations
        type_definition=textwrap.dedent(f"""\
            python class {arg_type.__name__} has this annotation:
            {arg_type.__annotations__}
            """)
        
    else:
        # Unknown types
        Warning(f"Unknown type {arg_type}. Keeping it as is.")
        type_definition = str(arg_type)

    return type_definition


def build_types_as_json_schema(arg_type):
    
    simple_types = {
        int: "integer",
        float: "number",
        str: "string",
        list: "array",
        bool: "boolean",
        dict: "object",
        set: "array",
        tuple: "array",
        frozenset: "array",
        bytes: "string",
    }
    
    return_type_schema = ""
    if arg_type in BASIC_TYPES:
        if not arg_type in simple_types:
            raise Exception(f"Unsupported type {arg_type}. Please use another type. Supported types are {simple_types.keys()}")
        else:
            return_type_schema = '{"type": "' + simple_types[arg_type] + '"}'
    else:
        # This is advanced types of user defined types
        return_type_schema = f"{describe_type_as_schema(arg_type)}"

    return return_type_schema

def nice_type_name(obj) -> str:
    """
    Get a nice name for the type to insert in function description for LLM.
    """
    if type(obj) is _alias:
        t=obj.__repr__()
        t=t.replace("typing.", "")
        return t
    
    if hasattr(obj, "__name__"):
        return obj.__name__

    return str(obj)