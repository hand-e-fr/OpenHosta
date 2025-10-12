from __future__ import annotations

import inspect
import json
import textwrap
import ast
import typing

from typing import Any
from dataclasses import is_dataclass
from enum import Enum 

from sys import version_info

from .pydantic_proxy import is_pydantic_available, BaseModel

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
    
    if expected_type is None \
        or expected_type is inspect._empty:
        typed_value = None

    elif expected_type in [Any]:
        
        # Try JSON
        if untyped_response.startswith("{"):
            try:
                typed_value = json.loads(untyped_response)                
            except json.JSONDecodeError as e:
                # Brocken JSON, keep as string
                typed_value = untyped_response
        else:
            typed_value = ast.literal_eval(untyped_response)

    elif expected_type is str:
        typed_value = untyped_response.strip("'").strip("\"")
    elif expected_type in [bytearray, frozenset, range]:
        typed_value = eval(untyped_response, {"bytearray": expected_type}, {})
        assert isinstance(typed_value, expected_type), f"Expected type {expected_type}, got {type(typed_value)}"
    elif expected_type in BASIC_TYPES:
        typed_value = ast.literal_eval(untyped_response)
        assert typed_value is None or isinstance(typed_value, expected_type), f"Expected type {expected_type}, got {type(typed_value)}"
    elif is_typing_type(expected_type):
        # Handle typing types
        origin = typing.get_origin(expected_type)
        args = typing.get_args(expected_type)
        
        if origin in [list, set, frozenset]:
            # List, Set, Frozenset
            item_type = args[0] if args else Any
            typed_value = eval(untyped_response, {origin.__name__: origin}, {})
            assert typed_value is None or isinstance(typed_value, origin), f"Expected type {origin}, got {type(typed_value)}"
            typed_value = origin([type_returned_data(repr(item), item_type) for item in typed_value])
        elif origin is tuple:
            # Tuple
            item_types = args if args else (Any,)
            typed_value = eval(untyped_response, {origin.__name__: origin}, {})
            assert typed_value is None or isinstance(typed_value, origin), f"Expected type {origin}, got {type(typed_value)}"
            if len(item_types) == 2 and item_types[1] is Ellipsis:
                # Tuple of variable length
                typed_value = origin([type_returned_data(repr(item), item_types[0]) for item in typed_value])
            else:
                # Tuple of fixed length
                if len(typed_value) != len(item_types):
                    raise TypeError(f"Expected tuple of length {len(item_types)}, got {len(typed_value)}")
                typed_value = origin([type_returned_data(repr(item), item_type) for item, item_type in zip(typed_value, item_types)])
        elif origin is dict:
            # Dict
            key_type = args[0] if args else Any
            value_type = args[1] if len(args) > 1 else Any
            if key_type is not str:
                raise TypeError("Only string keys are supported in Dict for type conversion.")
            typed_value = eval(untyped_response, {origin.__name__: origin}, {})
            assert isinstance(typed_value, origin), f"Expected type {origin}, got {type(typed_value)}"
            typed_value = {type_returned_data(repr(k), key_type): type_returned_data(repr(v), value_type) for k, v in typed_value.items()}
        
        else:
            # Unsupported typing type
            raise TypeError(f"Unsupported typing type: {expected_type}") 
    elif issubclass(expected_type, Enum):
        selected_value = untyped_response.strip("'").strip("\"")
        if selected_value.startswith(f"{expected_type.__name__}."):
            # LLM returned the enum member name
            typed_value = eval(selected_value, {expected_type.__name__: expected_type}, {})
        else:
            typed_value = None
            for member in list(expected_type):
                if selected_value == member.value:
                    typed_value = expected_type(selected_value)
                    break
                elif selected_value == member.name:
                    typed_value = eval(f"{expected_type.__name__}.{selected_value}", {expected_type.__name__: expected_type}, {})
                    break
        
    elif is_dataclass(expected_type):
        typed_value = eval(untyped_response, {expected_type.__name__: expected_type}, {})
        
    elif is_pydantic_available and issubclass(expected_type, BaseModel):
        if untyped_response.startswith("{"):
            dict_typed_value = None
            # Assume native python:
            try:
                dict_typed_value = ast.literal_eval(untyped_response)
            except Exception as e:
                pass
            
            # Or maybe JSON:
            try:
                dict_typed_value = json.loads(untyped_response)
            except Exception as e:
                pass
        
            if dict_typed_value is None:
                raise TypeError(f"Cannot convert response to pydantic model {expected_type.__name__}. use print_last_prompt to debug.")
            
            typed_value = expected_type(**dict_typed_value)
            
        elif untyped_response.startswith(expected_type.__name__):
            typed_value = eval(untyped_response, {expected_type.__name__: expected_type}, {})
        else:
            raise TypeError(f"Cannot convert response to pydantic model {expected_type.__name__}. use print_last_prompt to debug.")

    return typed_value

BASIC_TYPES = [
    int, float, complex, list, tuple, range, dict, set, frozenset,
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

    try:
        from PIL.Image import Image as PILImageType
        pil_available = True
    except:
        pil_available = False
    
    if arg_type in BASIC_TYPES or\
        is_typing_type(arg_type) or\
            arg_type == type:
        # Check if the type is a basic type or a typing alias
        type_definition = nice_type_name(arg_type)
    elif pil_available and issubclass(arg_type, PILImageType):
        pass
    elif issubclass(arg_type, Enum):
        type_definition = textwrap.dedent(f"""\
            # Python enum {arg_type.__name__} definition.
            # When you return a {arg_type.__name__}, print the enum member value as a string. I will identify the corresponding enum member.
            class {arg_type.__name__}({arg_type.__base__.__name__}):""")
        if arg_type.__doc__:
            type_definition += f'\n    """{arg_type.__doc__}"""'
        for member in arg_type:
            type_definition += f'\n    {member.name} = {repr(member.value)}'
        
        
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
    if arg_type is Any:
        return {}
    if arg_type is NoneType:
        return {"type": "null"}
    
    # Gestion des listes (List)
    if typing.get_origin(arg_type) in [list, set, tuple, frozenset]:
        # Récupère le type des éléments
        args =  typing.get_args(arg_type)
        item_type = args[0] if args else Any
        # Appelle récursivement la fonction pour obtenir le schéma des éléments
        items_schema = describe_type_as_schema(item_type)
        return {
            "type": "array",
            "items": items_schema
        }
        
    # Gestion des dictionnaires (Dict)
    elif typing.get_origin(arg_type) is dict:
        # Récupère les types de la clé et de la valeur
        args =  typing.get_args(arg_type)
        key_type = args[0] if args else Any
        value_type = args[1] if len(args) > 1 else Any

        if key_type is not str:
            raise TypeError("Only string keys are supported in Dict for JSON schema.")
        
        # Appelle récursivement la fonction pour obtenir le schéma des valeurs
        value_schema = describe_type_as_schema(value_type)
        return {
            "type": "object",
            "properties": {},
            "additionalProperties": value_schema
        }
    elif typing.get_origin(arg_type) is typing.Union:
        args = typing.get_args(arg_type)
        if len(args) == 2 and args[1] is type(None):
            return describe_type_as_schema(args[0])
        else:
            # Union of multiple types
            return {
                "anyOf": [describe_type_as_schema(arg) for arg in args]
            }
    elif typing.get_origin(arg_type) is typing.Literal:
        args = typing.get_args(arg_type)
        return {
            "enum": list(args)
        }
    elif typing.get_origin(arg_type) is typing.Annotated:
        args = typing.get_args(arg_type)
        return describe_type_as_schema(args[0])
    elif typing.get_origin(arg_type) is typing.TypeVar:
        args = typing.get_args(arg_type)
        if args:
            return {
                "anyOf": [describe_type_as_schema(arg) for arg in args]
            }
        else:
            return {}

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
        complex: "string",
        range: "string",
        bytearray: "string",
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

def nice_type_name(p_type) -> str:
    """
    Get a nice name for the type to insert in function description for LLM.
    """
    if is_typing_type(p_type):
        t=repr(p_type)
        t=t.replace("typing.", "")
        return t
    
    if hasattr(p_type, "__name__"):
        return p_type.__name__

    return str(p_type)