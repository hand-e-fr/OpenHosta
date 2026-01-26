
import typing
from typing import Sequence, Mapping, List, Dict, TypedDict
from OpenHosta.guarded.resolver import TypeResolver
from OpenHosta.guarded.subclassablecollections import GuardedList, GuardedDict

def test_resolve():
    print("Resolving Sequence[int]...")
    try:
        res = TypeResolver.resolve(Sequence[int])
        print(f"Result: {res}")
    except Exception as e:
        print(f"Error resolving Sequence[int]: {e}")
        import traceback
        traceback.print_exc()

    print("\nResolving Mapping[str, int]...")
    try:
        res = TypeResolver.resolve(Mapping[str, int])
        print(f"Result: {res}")
    except Exception as e:
        print(f"Error resolving Mapping[str, int]: {e}")
        traceback.print_exc()

    print("\nResolving TypedDict...")
    class MyTypedDict(TypedDict):
        x: int
    
    try:
        res = TypeResolver.resolve(MyTypedDict)
        print(f"Result: {res}")
    except Exception as e:
        print(f"Error resolving TypedDict: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_resolve()
