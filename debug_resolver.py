
import typing
import collections.abc
from typing import Sequence, Mapping, List, Dict, TypedDict, get_origin
from OpenHosta.guarded.resolver import TypeResolver

def debug_resolver():
    seq = Sequence[int]
    origin = get_origin(seq)
    print(f"Sequence origin: {origin}")
    print(f"origin == typing.Sequence: {origin == typing.Sequence}")
    print(f"origin == collections.abc.Sequence: {origin == collections.abc.Sequence}")
    
    map_type = Mapping[str, int]
    origin_map = get_origin(map_type)
    print(f"Mapping origin: {origin_map}")
    print(f"origin_map == typing.Mapping: {origin_map == typing.Mapping}")
    print(f"origin_map == collections.abc.Mapping: {origin_map == collections.abc.Mapping}")

    class MyTypedDict(TypedDict):
        x: int
    
    print(f"Is TypedDict type? {isinstance(MyTypedDict, type)}")
    print(f"Is TypedDict dict subclass? {issubclass(MyTypedDict, dict)}")
    try:
        from typing import is_typeddict
        print(f"is_typeddict: {is_typeddict(MyTypedDict)}")
    except ImportError:
        print("is_typeddict not available")

if __name__ == "__main__":
    debug_resolver()
