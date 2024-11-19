from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Union
from typing_extensions import TypedDict


class ExampleType(TypedDict):
    in_: Any
    out: Any


class CotType(TypedDict):
    task: str


class UseType(TypedDict):
    pass


MemKey = Literal["ex", "cot", "use"]
MemValue = Union[CotType, ExampleType, UseType]


@dataclass
class MemoryNode:
    key: MemKey
    id: int
    value: MemValue
