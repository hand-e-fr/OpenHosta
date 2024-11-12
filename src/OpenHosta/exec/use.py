from __future__ import annotations

from typing import Any, Callable, Union

from ..core.hosta import Hosta, UseType

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
    x = Hosta()
    x._bdy_add('use', UseType())
