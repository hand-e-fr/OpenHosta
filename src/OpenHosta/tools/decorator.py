"""The `@tool` decorator.

A tool is any callable with type hints + a docstring. `@tool` is optional sugar
that records metadata (a custom name, description, the `read_only` flag, and the
`requires` tags used by downstream permission policies). It never wraps the
function, so the callable keeps its identity, signature, and `__name__`.
"""
from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence, TypeVar, overload

F = TypeVar("F", bound=Callable[..., object])


@dataclass
class ToolMeta:
    name: str
    description: str
    read_only: bool = False  # used by downstream permission policies
    requires: frozenset[str] = field(default_factory=frozenset)  # capability tags a caller must hold


@overload
def tool(fn: F) -> F: ...
@overload
def tool(*, name: Optional[str] = ..., description: Optional[str] = ...,
         read_only: bool = ..., requires: Optional[Sequence[str]] = ...) -> Callable[[F], F]: ...


def tool(fn: Optional[F] = None, *, name: Optional[str] = None,
         description: Optional[str] = None, read_only: bool = False,
         requires: Optional[Sequence[str]] = None):
    """Attach `ToolMeta` to a callable. Usable bare (`@tool`) or with args
    (`@tool(read_only=True, requires=["admin"])`)."""
    def wrap(f: F) -> F:
        f.__hosta_tool__ = ToolMeta(  # type: ignore[attr-defined]
            name=name or f.__name__,
            description=description or (inspect.getdoc(f) or ""),
            read_only=read_only,
            requires=frozenset(requires or ()),
        )
        return f
    return wrap(fn) if fn is not None else wrap
