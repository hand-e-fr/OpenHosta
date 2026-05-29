"""The `@tool` decorator.

A tool is any callable with type hints + a docstring. `@tool` is optional sugar
that records metadata (a custom name, description, and the `read_only` flag used
by downstream permission policies). It never wraps the function, so the callable
keeps its identity, signature, and `__name__`.
"""
from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Callable, Optional, TypeVar, overload

F = TypeVar("F", bound=Callable[..., object])


@dataclass
class ToolMeta:
    name: str
    description: str
    read_only: bool = False  # used by downstream permission policies


@overload
def tool(fn: F) -> F: ...
@overload
def tool(*, name: Optional[str] = ..., description: Optional[str] = ...,
         read_only: bool = ...) -> Callable[[F], F]: ...


def tool(fn: Optional[F] = None, *, name: Optional[str] = None,
         description: Optional[str] = None, read_only: bool = False):
    """Attach `ToolMeta` to a callable. Usable bare (`@tool`) or with args
    (`@tool(read_only=True)`)."""
    def wrap(f: F) -> F:
        f.__hosta_tool__ = ToolMeta(  # type: ignore[attr-defined]
            name=name or f.__name__,
            description=description or (inspect.getdoc(f) or ""),
            read_only=read_only,
        )
        return f
    return wrap(fn) if fn is not None else wrap
