
import typing
from typing import Set, List, Dict, Union, Optional
from OpenHosta.guarded.primitives import GuardedPrimitive

def test_issubclass_crash():
    generics = [
        Set[int],
        List[int],
        Dict[str, int],
        Union[int, str],
        Optional[int]
    ]

    print(f"GuardedPrimitive: {GuardedPrimitive}")

    for gen in generics:
        print(f"\nTesting {gen}...")
        try:
            is_type = isinstance(gen, type)
            print(f"isinstance(gen, type): {is_type}")
            
            if is_type:
                print("Checking issubclass(gen, GuardedPrimitive)...")
                try:
                    res = issubclass(gen, GuardedPrimitive)
                    print(f"Result: {res}")
                except Exception as e:
                    print(f"CRASH in issubclass: {e}")
                    # Print detailed attributes of gen
                    try:
                        print(f"Has __mro__? {hasattr(gen, '__mro__')}")
                    except:
                        pass
        except Exception as e:
            print(f"Outer error: {e}")

if __name__ == "__main__":
    test_issubclass_crash()
