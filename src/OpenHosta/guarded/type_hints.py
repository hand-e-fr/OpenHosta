"""
Centralized helper for resolving type hints on structured types
(dataclasses, TypedDicts, Pydantic models).

Replaces the scattered `get_type_hints` calls throughout the guarded wrappers,
providing consistent error handling and string annotation resolution.
"""

import typing
import warnings
from typing import Any, Dict, Type


def resolve_struct_hints(cls: Type, fallback_annotations: bool = True) -> Dict[str, Any]:
    """Resolve type hints for a structured type (dataclass, TypedDict, Pydantic model).
    
    Tries `typing.get_type_hints(cls)` first. If that fails (e.g. due to missing
    imports or forward references), falls back to `cls.__annotations__` and attempts
    to resolve any remaining string annotations.
    
    Args:
        cls: The class to get type hints for.
        fallback_annotations: If True, fall back to __annotations__ on failure.
    
    Returns:
        A dict mapping field names to resolved Python types. All values are
        guaranteed to be real types (not strings), or `typing.Any` if unresolvable.
    """
    try:
        hints = typing.get_type_hints(cls)
        return hints
    except (NameError, AttributeError):
        # Expected when annotations reference undefined names or missing imports
        pass
    except Exception as e:
        warnings.warn(
            f"[OpenHosta] Unexpected error resolving type hints for {cls.__name__}: {e}"
        )
    
    if not fallback_annotations:
        return {}
    
    # Fall back to __annotations__ and resolve strings
    raw_annotations = getattr(cls, '__annotations__', {})
    if not raw_annotations:
        return {}
    
    # Try to resolve string annotations in the class's module namespace
    globalns = getattr(cls, '__module__', None)
    if globalns:
        import sys
        globalns = vars(sys.modules.get(globalns, {}))
    else:
        globalns = {}
    
    resolved = {}
    for name, annotation in raw_annotations.items():
        if isinstance(annotation, str):
            try:
                resolved[name] = eval(annotation, globalns)
            except Exception:
                warnings.warn(
                    f"[OpenHosta] Could not resolve annotation '{annotation}' "
                    f"for field '{name}' on {cls.__name__}. Falling back to Any."
                )
                resolved[name] = typing.Any
        else:
            resolved[name] = annotation
    
    return resolved

def extract_callable_args(annotation: Any) -> list:
    """
    Extracts the inner arguments from a typing.Callable annotation.
    Abstracts away the differences between Python 3.8 and 3.9+ implementations
    of Callable[[...], ...].
    
    Args:
        annotation: A typing.Callable or collections.abc.Callable annotation
        
    Returns:
        A flat list of argument types, typically with the return type at the end.
    """
    args = typing.get_args(annotation)
    if not args:
        return []
        
    extracted = []
    for a in args:
        if isinstance(a, list) or isinstance(a, tuple):
            for sub_a in a:
                if sub_a is not Ellipsis:
                    extracted.append(sub_a)
        elif a is not Ellipsis:
            extracted.append(a)
            
    return extracted
