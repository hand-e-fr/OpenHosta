from OpenHosta.guarded import GuardedEnum
from OpenHosta.guarded.resolver import TypeResolver
from enum import auto

class MyEnum(GuardedEnum):
    A1 = auto()
    A2 = auto()

def test():
    t = dict[tuple, dict[MyEnum, list[str]]]
    res = TypeResolver.resolve(t)
    print("Resolved Type:", res)
    print("_type_en:", res._type_en)

    t2 = tuple[MyEnum, str]
    res2 = TypeResolver.resolve(t2)
    print("Resolved Type 2:", res2)
    print("_type_en 2:", res2._type_en)

if __name__ == "__main__":
    test()
