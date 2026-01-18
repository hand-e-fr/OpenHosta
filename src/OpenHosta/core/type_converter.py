from __future__ import annotations

import inspect
import json
import textwrap
import ast
import typing
import types

from typing import Any
from dataclasses import is_dataclass
from enum import Enum 

from sys import version_info

from .pydantic_proxy import is_pydantic_available, BaseModel
from .pydantic_proxy import reconstruct_pydantic_class_string_auto

from ..semantics.resolver import TypeResolver

if version_info.major == 3 and version_info.minor > 9:
    from types import NoneType
else:
    NoneType = type(None)


def type_returned_data(untyped_response: str, expected_type: type) -> Any:
    """
    Convert the untyped response to the expected type.
    """
    
    semantic_type = TypeResolver.resolve(expected_type)
    convertion_report = semantic_type.attempt(untyped_response)
    return convertion_report.unwrap()
    
def describe_type_as_python(arg_type):

    semantic_type = TypeResolver.resolve(arg_type)
    return semantic_type._type_py


def is_typing_type(arg_type):
    # Check if the type provided as argument exist in typing library
    return str(arg_type).startswith("typing.")


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