# mypy: ignore-errors
"""Guarded wrapper — value proxy with metadata tracking.

This module provides the `Guarded[T]` wrapper class and `GuardMetadata`
dataclass used by the guarded test suite.  It sits alongside the existing
guarded primitives and is exposed through the canonical ``openhosta``
namespace.
"""

from __future__ import annotations

import dataclasses
import inspect
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TypeVar, get_origin, get_args, Union as TypingUnion

T = TypeVar("T")


@dataclass
class GuardMetadata:
    """Lightweight metadata attached to a Guarded value.

    Parameters
    ----------
    uncertainty : float
        Estimated uncertainty (0.0 = fully certain, 1.0 = fully uncertain).
    time_consumed : float
        Milliseconds spent producing the value.
    logs : list[str]
        Free-form log entries.
    sources : list[str]
        Provenance / source identifiers.
    llm_logs : list[dict]
        LLM call log entries.
    heal_traces : list[str]
        Healing trace entries.
    """

    uncertainty: float = 0.0
    time_consumed: float = 0.0
    logs: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    llm_logs: list[dict] = field(default_factory=list)
    heal_traces: list[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        """Return ``True`` when every field is at its default (empty) value."""
        return (
            self.uncertainty == 0.0
            and self.time_consumed == 0.0
            and len(self.logs) == 0
            and len(self.sources) == 0
            and len(self.llm_logs) == 0
            and len(self.heal_traces) == 0
        )

    def merge(self, other: GuardMetadata) -> GuardMetadata:
        """Return a new GuardMetadata with aggregated values."""
        return GuardMetadata(
            uncertainty=self.uncertainty + other.uncertainty,
            time_consumed=self.time_consumed + other.time_consumed,
            logs=self.logs + other.logs,
            sources=self.sources + other.sources,
            llm_logs=self.llm_logs + other.llm_logs,
            heal_traces=self.heal_traces + other.heal_traces,
        )


class Guarded[T]:
    """Proxy wrapper that delegates every operation to the underlying value.

    Parameters
    ----------
    value : T
        The wrapped value.
    metadata : GuardMetadata, optional
        Associated metadata.  Defaults to an empty :class:`GuardMetadata`.
    """

    __slots__ = ("_value", "_metadata")

    def __init__(self, value: T, metadata: GuardMetadata | None = None) -> None:
        object.__setattr__(self, "_value", value)
        object.__setattr__(self, "_metadata", metadata or GuardMetadata())

    # -- attribute delegation --------------------------------------------------

    def __getattr__(self, name: str) -> Any:
        val = object.__getattribute__(self, "_value")
        return getattr(val, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("_value", "_metadata"):
            object.__setattr__(self, name, value)
        else:
            setattr(self._value, name, value)

    def __delattr__(self, name: str) -> None:
        if name in ("_value", "_metadata"):
            raise AttributeError(name)
        delattr(self._value, name)

    # -- comparison ------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        lhs = self._value if isinstance(self._value, Guarded) else self._value
        rhs = other._value if isinstance(other, Guarded) else other
        return lhs == rhs

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: object) -> bool:
        rhs = other._value if isinstance(other, Guarded) else other
        return self._value < rhs

    def __le__(self, other: object) -> bool:
        rhs = other._value if isinstance(other, Guarded) else other
        return self._value <= rhs

    def __gt__(self, other: object) -> bool:
        rhs = other._value if isinstance(other, Guarded) else other
        return self._value > rhs

    def __ge__(self, other: object) -> bool:
        rhs = other._value if isinstance(other, Guarded) else other
        return self._value >= rhs

    # -- arithmetic ------------------------------------------------------------

    def _arith(self, op: str, other: object) -> Any:
        rhs = other._value if isinstance(other, Guarded) else other
        return getattr(self._value, op)(rhs)

    def __add__(self, other: object) -> Any:
        return self._arith("__add__", other)

    def __radd__(self, other: object) -> Any:
        lhs = other if not isinstance(other, Guarded) else other._value
        return lhs + self._value

    def __sub__(self, other: object) -> Any:
        return self._arith("__sub__", other)

    def __rsub__(self, other: object) -> Any:
        lhs = other if not isinstance(other, Guarded) else other._value
        return lhs - self._value

    def __mul__(self, other: object) -> Any:
        return self._arith("__mul__", other)

    def __rmul__(self, other: object) -> Any:
        lhs = other if not isinstance(other, Guarded) else other._value
        return lhs * self._value

    def __truediv__(self, other: object) -> Any:
        return self._arith("__truediv__", other)

    def __rtruediv__(self, other: object) -> Any:
        lhs = other if not isinstance(other, Guarded) else other._value
        return lhs / self._value

    def __floordiv__(self, other: object) -> Any:
        return self._arith("__floordiv__", other)

    def __mod__(self, other: object) -> Any:
        return self._arith("__mod__", other)

    def __pow__(self, other: object, *args: Any) -> Any:
        rhs = other._value if isinstance(other, Guarded) else other
        if args:
            return self._value ** rhs % args[0]
        return self._value ** rhs

    def __neg__(self) -> Any:
        return -self._value

    def __pos__(self) -> Any:
        return +self._value

    def __abs__(self) -> Any:
        return abs(self._value)

    # -- container protocols ---------------------------------------------------

    def __len__(self) -> int:
        return len(self._value)

    def __iter__(self):
        return iter(self._value)

    def __contains__(self, item: object) -> bool:
        return item in self._value

    def __getitem__(self, key: Any) -> Any:
        return self._value[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        self._value[key] = value

    def __delitem__(self, key: Any) -> None:
        del self._value[key]

    # -- identity / repr -------------------------------------------------------

    def __bool__(self) -> bool:
        return bool(self._value)

    # -- Guarded-specific methods (not delegated) ------------------------------

    def unwrap(self) -> T:
        """Return the underlying unwrapped value."""
        return object.__getattribute__(self, "_value")

    @property
    def uncertainty(self) -> float:
        return object.__getattribute__(self, "_metadata").uncertainty

    @property
    def abstraction_level(self) -> str:
        return "native"

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return repr(self._value)

    def __str__(self) -> str:
        return str(self._value)

    def __format__(self, format_spec: str) -> str:
        return format(self._value, format_spec)

    def __index__(self) -> int:
        return self._value.__index__()  # type: ignore[union-attr]

    # -- callable --------------------------------------------------------------

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._value(*args, **kwargs)

 # --------------------------------------------------------------------------- #
# guard / unguard helpers                                                      #
# --------------------------------------------------------------------------- #


def guard(
    value: Any,
    metadata: GuardMetadata | None = None,
) -> Any:
    """Wrap *value* in a :class:`Guarded` proxy.

    Primitives → Guarded, lists/dicts/tuples → recursively wrapped,
    dataclasses → wrapped with per-field aggregation.
    Already-Guarded values are returned unchanged.
    """
    meta = metadata or GuardMetadata()

    if isinstance(value, Guarded):
        return value

    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        wrapped_fields = {}
        agg = GuardMetadata()
        for f in dataclasses.fields(value):
            fv = getattr(value, f.name)
            if isinstance(fv, Guarded):
                wrapped_fields[f.name] = fv
                agg = agg.merge(fv._metadata)
            else:
                wrapped_fields[f.name] = guard(fv)
                agg = agg.merge(wrapped_fields[f.name]._metadata)
        agg = meta.merge(agg)
        wrapped = dataclasses.replace(value, **wrapped_fields)
        return Guarded(wrapped, agg)

    if isinstance(value, dict):
        wrapped = {}
        agg = GuardMetadata()
        for k, v in value.items():
            if isinstance(v, Guarded):
                wrapped[k] = v
                agg = agg.merge(v._metadata)
            else:
                wrapped[k] = guard(v)
                agg = agg.merge(wrapped[k]._metadata)
        agg = meta.merge(agg)
        return Guarded(wrapped, agg)

    if isinstance(value, (list, tuple)):
        wrapped = []
        agg = GuardMetadata()
        for item in value:
            if isinstance(item, Guarded):
                wrapped.append(item)
                agg = agg.merge(item._metadata)
            else:
                g = guard(item)
                wrapped.append(g)
                agg = agg.merge(g._metadata)
        agg = meta.merge(agg)
        result = Guarded(type(value)(wrapped), agg)
        return result

    return Guarded(value, meta)


def unguard(value: Any) -> Any:
    """Recursively unwrap :class:`Guarded` proxies to native types."""
    if isinstance(value, Guarded):
        return unguard(value._value)

    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return type(value)(**{
            f.name: unguard(getattr(value, f.name))
            for f in dataclasses.fields(value)
        })

    if isinstance(value, dict):
        return {k: unguard(v) for k, v in value.items()}

    if isinstance(value, (list, tuple)):
        return type(value)(unguard(item) for item in value)

    return value


def guard_info(value: Any) -> GuardMetadata:
    """Return aggregated :class:`GuardMetadata` for a value tree.

    For a :class:`Guarded` leaf, returns its ``_metadata``.
    For containers, aggregates (sums) the metadata of all Guarded descendants.
    For native values, returns an empty :class:`GuardMetadata`.
    """
    if isinstance(value, Guarded):
        return value._metadata

    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return _agg_guard_info([
            guard_info(getattr(value, f.name))
            for f in dataclasses.fields(value)
        ])

    if isinstance(value, dict):
        return _agg_guard_info([
            guard_info(v) for v in value.values()
        ])

    if isinstance(value, (list, tuple)):
        return _agg_guard_info([
            guard_info(item) for item in value
        ])

    return GuardMetadata()


def _agg_guard_info(metas: list[GuardMetadata]) -> GuardMetadata:
    """Sum uncertainties and time, concatenate lists."""
    if not metas:
        return GuardMetadata()
    total_unc = sum(m.uncertainty for m in metas)
    total_time = sum(m.time_consumed for m in metas)
    all_logs = []
    all_sources = []
    all_llm = []
    all_heal = []
    for m in metas:
        all_logs.extend(m.logs)
        all_sources.extend(m.sources)
        all_llm.extend(m.llm_logs)
        all_heal.extend(m.heal_traces)
    return GuardMetadata(
        uncertainty=total_unc,
        time_consumed=total_time,
        logs=all_logs,
        sources=all_sources,
        llm_logs=all_llm,
        heal_traces=all_heal,
    )


# --------------------------------------------------------------------------- #
# Tri-modal serialization helpers                                              #
# --------------------------------------------------------------------------- #


def _unwrap_guarded(obj: Any) -> Any:
    """If obj is Guarded, return inner value; otherwise return as-is."""
    if isinstance(obj, Guarded):
        return obj._value
    return obj


def _type_name(t: type) -> str:
    """Get a readable type name for annotations."""
    if hasattr(t, "__name__"):
        return t.__name__
    return str(t)


# -- guarded_to_python -------------------------------------------------------


def guarded_to_python(obj: Any) -> str:
    """Generate a Python source-code representation of *obj*.

    Handles functions, dataclass types, enum types, primitive values,
    and Guarded wrappers.
    """
    obj = _unwrap_guarded(obj)

    # Function / callable (not a type)
    if callable(obj) and not isinstance(obj, type):
        try:
            sig = inspect.signature(obj)
        except ValueError:
            sig = inspect.Signature()
        params = ", ".join(
            f"{p.name}: {p.annotation.__name__ if p.annotation is not inspect.Parameter.empty else 'Any'}"
            for p in sig.parameters.values()
        )
        ret = sig.return_annotation.__name__ if sig.return_annotation is not inspect.Signature.empty else "Any"
        lines = [f"def {obj.__name__}({params}) -> {ret}:"]
        doc = (obj.__doc__ or "").strip().split("\n")[0]
        if doc:
            lines.append(f'    """{doc}"""')
        try:
            src = inspect.getsource(obj)
            body = src.split(":", 1)[1].strip()
            body_lines = [line for line in body.split("\n") if line.strip() and not line.strip().startswith('"""')]
            if body_lines:
                lines.append(f"    {body_lines[0].strip()}")
        except (OSError, TypeError):
            if obj.__name__ == "<lambda>":
                lines.append("    <lambda body>")
            else:
                lines.append("    ...")
        return "\n".join(lines)

    # Enum type
    if isinstance(obj, type) and issubclass(obj, Enum):
        lines = [f"class {obj.__name__}(Enum):"]
        for member in obj:
            val = repr(member.value)
            lines.append(f"    {member.name} = {val}")
        return "\n".join(lines)

    # Dataclass type
    if isinstance(obj, type) and dataclasses.is_dataclass(obj):
        lines = ["@dataclasses.dataclass", f"class {obj.__name__}:"]
        doc = (obj.__doc__ or "").strip().split("\n")[0]
        if doc:
            lines.append(f'    """{doc}"""')
        for f in dataclasses.fields(obj):
            ann = f.type if hasattr(f.type, "__name__") else str(f.type)
            lines.append(f"    {f.name}: {ann}")
        return "\n".join(lines)

    # Dataclass instance
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        cls_name = type(obj).__name__
        lines = [f"{cls_name}("]
        for f in dataclasses.fields(obj):
            val = repr(getattr(obj, f.name))
            lines.append(f"    {f.name}={val},")
        lines.append(")")
        return "\n".join(lines)

    # Primitive value
    type_map = {str: "str", int: "int", float: "float", bool: "bool"}
    tn = type_map.get(type(obj), type(obj).__name__)
    return f"type: {tn}\nvalue: {repr(obj)}"


# -- guarded_to_json ---------------------------------------------------------


def guarded_to_json(obj: Any) -> dict:
    """Generate a JSON Schema dict for *obj*.

    Handles primitives, enum types, dataclass types, and Guarded wrappers.
    """
    obj = _unwrap_guarded(obj)

    # Enum type
    if isinstance(obj, type) and issubclass(obj, Enum):
        members = list(obj)
        if not members:
            val_type = "string"
        else:
            val_type = type(members[0].value).__name__
        type_map = {"str": "string", "int": "integer", "float": "number"}
        return {
            "type": type_map.get(val_type, val_type),
            "enum": [m.value for m in members],
            "title": obj.__name__,
        }

    # Dataclass type
    if isinstance(obj, type) and dataclasses.is_dataclass(obj):
        properties: dict[str, dict] = {}
        required: list[str] = []
        for f in dataclasses.fields(obj):
            ann = f.type
            properties[f.name] = guarded_to_json(ann)
            required.append(f.name)
        doc = (obj.__doc__ or "").strip().split("\n")[0]
        result: dict[str, Any] = {
            "type": "object",
            "title": obj.__name__,
            "properties": properties,
            "required": required,
        }
        if doc:
            result["description"] = doc
        return result

    # Subscripted generics: list[T], dict[K, V], set[T], tuple[T, ...], Union / Optional
    origin = get_origin(obj)
    if origin is not None:
        args = get_args(obj)

        if origin is list or origin is list:
            inner = guarded_to_json(args[0]) if args else {"type": "string"}
            return {"type": "array", "items": inner}

        if origin is dict or origin is dict:
            if args and len(args) == 2:
                return {
                    "type": "object",
                    "additionalProperties": guarded_to_json(args[1]),
                }
            return {"type": "object"}

        if origin is set or origin is set:
            inner = guarded_to_json(args[0]) if args else {"type": "string"}
            return {"type": "array", "items": inner}

        if origin is tuple or origin is tuple:
            if args:
                # Filter out Ellipsis for variable-length tuples
                if Ellipsis in args:
                    inner = guarded_to_json(args[0])
                    return {"type": "array", "items": inner}
                items = [guarded_to_json(a) for a in args]
                return {"type": "array", "prefixItems": items}
            return {"type": "array"}

        # Union / Optional — describe as any-of
        import types

        if origin is TypingUnion or (hasattr(types, "UnionType") and origin is types.UnionType):
            non_none = [a for a in args if a is not type(None)]
            has_none = any(a is type(None) for a in args)
            options = [guarded_to_json(a) for a in non_none]
            if len(options) == 1 and has_none:
                return {**options[0], "nullable": True}
            if options:
                return {"anyOf": options}
            return {"type": "null"}

    # Built-in type objects (str, int, float, bool, etc.)
    if isinstance(obj, type):
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            type(None): "null",
        }
        tn = type_map.get(obj, "object")
        return {"type": tn, "title": obj.__name__}

    # Dataclass instance — treat as its type
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return guarded_to_json(type(obj))

    # Primitives (bool must be checked before int!)
    if obj is None:
        return {"type": "null"}
    if isinstance(obj, bool):
        return {"type": "boolean"}
    if isinstance(obj, int):
        return {"type": "integer"}
    if isinstance(obj, float):
        return {"type": "number"}
    if isinstance(obj, str):
        return {"type": "string"}

    # Fallback
    return {"type": "object"}


def _json_type_name(t: Any) -> str:
    """Map a Python type annotation to a JSON Schema type name."""
    if hasattr(t, "__name__"):
        tn = t.__name__
        type_map = {"str": "string", "int": "integer", "float": "number", "bool": "boolean"}
        return type_map.get(tn, tn)
    return str(t)


# -- guarded_to_markdown -----------------------------------------------------


def guarded_to_markdown(obj: Any) -> str:
    """Generate a Markdown representation of *obj*.

    Handles dataclass types, enum types, functions, primitives,
    and Guarded wrappers.
    """
    obj = _unwrap_guarded(obj)

    # Function
    if callable(obj) and not isinstance(obj, type):
        try:
            sig = inspect.signature(obj)
        except ValueError:
            sig = inspect.Signature()
        params_str = str(sig)
        lines = [f"# {obj.__name__}", "", f"**Signature:** `def {obj.__name__}({params_str})`"]
        doc = (obj.__doc__ or "").strip()
        if doc:
            lines.extend(["", f">{doc}"])
        lines.append("")
        return "\n".join(lines)

    # Enum type
    if isinstance(obj, type) and issubclass(obj, Enum):
        lines = [f"# {obj.__name__}", ""]
        for member in obj:
            lines.append(f"- `{member.value}`: **{member.name}**")
        lines.append("")
        return "\n".join(lines)

   # Dataclass type
    if isinstance(obj, type) and dataclasses.is_dataclass(obj):
        lines = [f"# {obj.__name__}", ""]
        doc = (obj.__doc__ or "").strip().split("\n")[0]
        if doc:
            lines.extend([f">{doc}", ""])
        for f in dataclasses.fields(obj):
            ann = f.type
            if hasattr(ann, "__name__"):
                tn = ann.__name__
            else:
                tn = str(ann)
            lines.append(f"- **{f.name}** (`{tn}`)")
        lines.append("")
        return "\n".join(lines)

    # Dataclass instance
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        cls_name = type(obj).__name__
        lines = [f"# {cls_name} instance", ""]
        for f in dataclasses.fields(obj):
            val = getattr(obj, f.name)
            lines.append(f"- **{f.name}**: `{val}`")
        lines.append("")
        return "\n".join(lines)

    # Primitive
    type_map = {str: "str", int: "int", float: "float", bool: "bool"}
    tn = type_map.get(type(obj), type(obj).__name__)
    return f"# Value\n\n`{repr(obj)}` (`{tn}`)"
