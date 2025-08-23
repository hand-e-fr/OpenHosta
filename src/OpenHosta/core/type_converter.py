from __future__ import annotations

import inspect
import json
import textwrap
import ast
import typing

from typing import Any
from dataclasses import is_dataclass

import sys
from sys import version_info

from .pydantic_proxy import is_pydantic_available, BaseModel, convert_pydantic

if version_info.major == 3 and version_info.minor > 9:
    from types import NoneType
else:
    NoneType = type(None)

def is_typing_type(arg_type):
    # Check if the type provided as argument exist in typing library
    return str(arg_type).startswith("typing.")

def type_returned_data(untyped_response: str, expected_type: type) -> Any:
    """
    Convert the untyped response to the expected type.
    """
    
    typed_value = None
    
    if expected_type in BASIC_TYPES:
        try:
            typed_value = expected_type(untyped_response)
        except (ValueError, TypeError):
            # If conversion fails, keep as string
            pass
        
        if typed_value is None:
            # try with safe eval for python types
            try:
                typed_value = ast.literal_eval(untyped_response)
                assert isinstance(typed_value, expected_type)
            except (ValueError, SyntaxError):
                # If eval fails, keep as string
                typed_value = untyped_response

    elif is_pydantic_available and issubclass(expected_type, BaseModel):
         typed_value = convert_pydantic(json.loads(untyped_response), expected_type)

    return typed_value

BASIC_TYPES = [
    int, float, complex, str, list, tuple, range, dict, set, frozenset,
    bool, bytes, bytearray, memoryview
]

def describe_type_as_schema(arg_type):
    """
    Describe a Python type as a JSON schema.
    """
    # Check if arg_type is pydantic model
    if is_pydantic_available and issubclass(arg_type, BaseModel):
        response = arg_type.model_json_schema()
    elif arg_type in BASIC_TYPES:
        response = build_types_as_json_schema(arg_type)
    elif is_typing_type(arg_type):
        response = build_typing_as_json_schema(arg_type)
    else:
        response = {"type": "string"}

    return response

def describe_type_as_python(arg_type):
    type_definition = None
    
    if arg_type in BASIC_TYPES or\
        is_typing_type(arg_type) or\
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

def build_typing_as_json_schema(arg_type):
    """
    Génère un schéma JSON à partir d'un type Python (typing).
    Gère les types de base (int, str, bool), List et Dict.
    """
    
    # Types de base
    if arg_type is int:
        return {"type": "integer"}
    if arg_type is str:
        return {"type": "string"}
    if arg_type is bool:
        return {"type": "boolean"}
    if arg_type is float:
        return {"type": "number"}
    
    # Gestion des listes (List)
    if typing.get_origin(arg_type) is list:
        # Récupère le type des éléments de la liste
        item_type = typing.get_args(arg_type)[0]
        # Appelle récursivement la fonction pour obtenir le schéma des éléments
        items_schema = build_typing_as_json_schema(item_type)
        return {
            "type": "array",
            "items": items_schema
        }
        
    # Gestion des dictionnaires (Dict)
    if typing.get_origin(arg_type) is dict:
        # Récupère les types de la clé et de la valeur
        key_type, value_type = typing.get_args(arg_type)
        # S'assure que les clés sont des chaînes (exigence de JSON)
        if key_type is not str:
            raise TypeError("JSON keys must be strings.")
        
        # Appelle récursivement la fonction pour obtenir le schéma des valeurs
        value_schema = build_typing_as_json_schema(value_type)
        return {
            "type": "object",
            "properties": {},
            "additionalProperties": value_schema
        }

    raise TypeError(f"Type '{arg_type}' is not supported.")


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
    if is_typing_type(obj):
        t=obj.__repr__()
        t=t.replace("typing.", "")
        return t
    
    if hasattr(obj, "__name__"):
        return obj.__name__

    return str(obj)