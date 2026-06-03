# mypy: ignore-errors
"""
Centralized helper for resolving type hints on structured types
(dataclasses, TypedDicts, Pydantic models).

Replaces the scattered `get_type_hints` calls throughout the guarded wrappers,
providing consistent error handling and string annotation resolution.
"""

import inspect
import typing
import warnings
from typing import Any


def nice_type_name(p_type: Any) -> str:
    """
    Get a nice name for the type to insert in function description for LLM.
    (Migrated from core.analizer to remove V4 dependency.)
    """
    if p_type is None or p_type is inspect._empty:
        return "Any"

    # Handle Python 3.12 TypeAliasType
    if hasattr(p_type, "__name__") and type(p_type).__name__ == "TypeAliasType":
        return p_type.__name__

    # Handle Guarded Types
    from .primitives import GuardedPrimitive
    if isinstance(p_type, type):
        if issubclass(p_type, GuardedPrimitive):
            if hasattr(p_type, "_item_type") and p_type._item_type:
                return f"{p_type.__name__}[{nice_type_name(p_type._item_type)}]"
            if hasattr(p_type, "_item_types") and p_type._item_types:
                return f"{p_type.__name__}[{', '.join(nice_type_name(t) for t in p_type._item_types)}]"
            if hasattr(p_type, "_key_type") and p_type._key_type and hasattr(p_type, "_value_type") and p_type._value_type:
                return f"{p_type.__name__}[{nice_type_name(p_type._key_type)}, {nice_type_name(p_type._value_type)}]"
            name = p_type.__name__
            if name.startswith("Guarded_") and len(name) > 8:
                return name[8:]
            return name

    # Handle Guarded[T] - unwrap to inner type for cleaner display
    if hasattr(p_type, "__origin__"):
        from .primitives import Guarded as GuardedPrimitiveMarker
        from .wrapper import Guarded as GuardedWrapper
        origin = p_type.__origin__
        if origin is GuardedPrimitiveMarker or origin is GuardedWrapper:
            args = getattr(p_type, "__args__", ())
            if args:
                return nice_type_name(args[0])

    # Handle typing types and GenericAlias (tuple[int, ...], List[str], etc.)
    if str(p_type).startswith("typing.") or hasattr(p_type, "__origin__"):
        t = repr(p_type)
        t = t.replace("typing.", "")
        t = t.replace("collections.abc.", "")
        t = t.replace("builtins.", "")
        t = t.replace("openhosta.guarded.primitives.", "")
        return t

    if hasattr(p_type, "__name__"):
        return p_type.__name__

    return str(p_type)


def resolve_struct_hints(cls: type, fallback_annotations: bool = True) -> dict[str, Any]:
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
            f"[OpenHosta] Unexpected error resolving type hints for {cls.__name__}: {e}", stacklevel=2
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
                    f"for field '{name}' on {cls.__name__}. Falling back to Any.", stacklevel=2
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
