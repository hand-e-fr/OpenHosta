from __future__ import annotations

from typing import Any, Callable, Union

from ..core.hosta_inspector import HostaInspector, UseType

all = (
    "use",
    "VAR",
    "TOOL",
    "RAG",
    "DB"
)


class VAR:
    pass


class TOOL:
    pass


class RAG:
    pass


class DB:
    pass


def use(obj: Union[Callable, Any], typ: Union[VAR, TOOL, RAG, DB], title: str):
    x = HostaInspector()
    x._bdy_add('use', UseType())
