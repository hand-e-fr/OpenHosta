from __future__ import annotations

from typing import Any, Literal, Union, TypedDict

class ExampleType(TypedDict):
    in_: Any
    out: Any

class CotType(TypedDict):
    task: str
 
class UseType(TypedDict):
    pass

MemKey = Literal["ex", "cot", "use"]
MemValue = Union[CotType, ExampleType, UseType]
    
class MemoryNode:
    key:MemKey
    id:int
    value:MemValue

