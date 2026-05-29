"""`tool_to_schema(fn)` — turn a callable into an OpenAI-compatible function schema.

Parameters are read from the signature + type hints; the description comes from
`@tool` metadata (or the docstring). Python type hints are mapped to JSON Schema
with a small, dependency-free resolver that covers the cases tool arguments use in
practice: scalars, list/dict, Optional/Union, Literal and Enum. Anything exotic
degrades gracefully to a permissive `{}` schema rather than failing.
"""
from __future__ import annotations

import enum
import inspect
import typing
from typing import Any, Dict, List, get_args, get_origin

from .decorator import ToolMeta

_SCALARS: Dict[type, str] = {
    str: "string",
    bool: "boolean",
    int: "integer",
    float: "number",
}


def _meta_from_fn(fn: Any) -> ToolMeta:
    return ToolMeta(name=fn.__name__, description=inspect.getdoc(fn) or "")


def _enum_schema(values: List[Any]) -> Dict[str, Any]:
    """An ``enum`` schema, inferring ``type`` when all values share one scalar type."""
    schema: Dict[str, Any] = {"enum": values}
    types = {type(v) for v in values}
    if len(types) == 1 and next(iter(types)) in _SCALARS:
        schema["type"] = _SCALARS[next(iter(types))]
    return schema


def _py_type_to_schema(hint: Any) -> Dict[str, Any]:
    """Best-effort map of a Python type hint to a JSON Schema fragment."""
    if hint is Any or hint is None or hint is inspect.Parameter.empty:
        return {}
    if hint in _SCALARS:
        return {"type": _SCALARS[hint]}

    origin = get_origin(hint)
    args = get_args(hint)

    # Optional[X] / Union[...] -> drop NoneType; collapse to single or anyOf.
    if origin is typing.Union or origin is getattr(__import__("types"), "UnionType", None):
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return _py_type_to_schema(non_none[0])
        return {"anyOf": [_py_type_to_schema(a) for a in non_none]}

    # Literal[...] -> enum. Enum *members* are unwrapped to their (JSON-able) value.
    if origin is typing.Literal:
        values = [a.value if isinstance(a, enum.Enum) else a for a in args]
        return _enum_schema(values)

    if origin in (list, set, frozenset):
        item = args[0] if args else Any
        return {"type": "array", "items": _py_type_to_schema(item)}

    if origin is tuple:
        # Tuple[X, ...] or a homogeneous tuple -> typed array; mixed fixed tuple ->
        # plain array (JSON Schema can't faithfully model heterogeneous positions here).
        if len(args) == 2 and args[1] is Ellipsis:
            return {"type": "array", "items": _py_type_to_schema(args[0])}
        if args and len(set(args)) == 1:
            return {"type": "array", "items": _py_type_to_schema(args[0])}
        return {"type": "array"}

    if origin is dict:
        return {"type": "object"}

    if isinstance(hint, type) and issubclass(hint, enum.Enum):
        return _enum_schema([m.value for m in hint])

    if isinstance(hint, type) and hint in _SCALARS:
        return {"type": _SCALARS[hint]}

    return {}  # unknown -> permissive


def tool_to_schema(fn: Any) -> Dict[str, Any]:
    """Return an OpenAI-compatible `{"type": "function", "function": {...}}` schema."""
    meta: ToolMeta = getattr(fn, "__hosta_tool__", None) or _meta_from_fn(fn)
    sig = inspect.signature(fn)
    try:
        hints = typing.get_type_hints(fn)
    except Exception:
        hints = getattr(fn, "__annotations__", {})

    props: Dict[str, Any] = {}
    required: List[str] = []
    for pname, p in sig.parameters.items():
        if pname == "self" or p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
            continue
        props[pname] = _py_type_to_schema(hints.get(pname, str))
        if p.default is inspect.Parameter.empty:
            required.append(pname)

    return {
        "type": "function",
        "function": {
            "name": meta.name,
            "description": meta.description,
            "parameters": {"type": "object", "properties": props, "required": required},
        },
    }
