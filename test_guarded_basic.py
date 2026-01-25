"""
Tests basiques pour vérifier le fonctionnement du module guarded.
"""
import sys
sys.path.insert(0, '/home/ebatt/VSCode_GitRepos/OpenHosta.git/src')

# Test des imports directs (sans passer par __init__.py)
print("Testing imports...")
from OpenHosta.guarded.primitives import GuardedPrimitive, ProxyWrapper
from OpenHosta.guarded.constants import Tolerance
from OpenHosta.guarded.subclassablescalars import GuardedInt, GuardedFloat, GuardedUtf8
from OpenHosta.guarded.subclassablewithproxy import GuardedBool, GuardedNone
from OpenHosta.guarded.subclassablecollections import GuardedList, GuardedDict, GuardedSet, GuardedTuple
from OpenHosta.guarded.subclassableclasses import GuardedEnum
print("✅ All imports successful\n")

# Test GuardedInt
print("Testing GuardedInt...")
age = GuardedInt("42")
assert age == 42
assert age.uncertainty <= Tolerance.STRICT
print(f"  GuardedInt('42') = {age}, uncertainty={age.uncertainty}, level={age.abstraction_level}")

age2 = GuardedInt("1,000")
assert age2 == 1000
print(f"  GuardedInt('1,000') = {age2}, uncertainty={age2.uncertainty}, level={age2.abstraction_level}")
print("✅ GuardedInt works\n")

# Test GuardedFloat
print("Testing GuardedFloat...")
pi = GuardedFloat("3,14")
assert abs(pi - 3.14) < 0.01
print(f"  GuardedFloat('3,14') = {pi}, uncertainty={pi.uncertainty}, level={pi.abstraction_level}")
print("✅ GuardedFloat works\n")

# Test GuardedUtf8
print("Testing GuardedUtf8...")
text = GuardedUtf8("hello")
assert text == "hello"
print(f"  GuardedUtf8('hello') = {text}, uncertainty={text.uncertainty}, level={text.abstraction_level}")
print("✅ GuardedUtf8 works\n")

# Test GuardedBool
print("Testing GuardedBool...")
b1 = GuardedBool("yes")
assert b1.unwrap() == True
print(f"  GuardedBool('yes') = {b1.unwrap()}, uncertainty={b1.uncertainty}, level={b1.abstraction_level}")

b2 = GuardedBool("non")
assert b2.unwrap() == False
print(f"  GuardedBool('non') = {b2.unwrap()}, uncertainty={b2.uncertainty}, level={b2.abstraction_level}")
print("✅ GuardedBool works\n")

# Test GuardedNone
print("Testing GuardedNone...")
n = GuardedNone("null")
assert n.unwrap() is None
print(f"  GuardedNone('null') = {n.unwrap()}, uncertainty={n.uncertainty}, level={n.abstraction_level}")
print("✅ GuardedNone works\n")

# Test GuardedList
print("Testing GuardedList...")
lst = GuardedList([1, 2, 3])
assert lst == [1, 2, 3]
print(f"  GuardedList([1, 2, 3]) = {lst}, uncertainty={lst.uncertainty}, level={lst.abstraction_level}")
print("✅ GuardedList works\n")

# Test GuardedDict
print("Testing GuardedDict...")
d = GuardedDict({"a": 1, "b": 2})
assert d == {"a": 1, "b": 2}
print(f"  GuardedDict({{'a': 1, 'b': 2}}) = {d}, uncertainty={d.uncertainty}, level={d.abstraction_level}")
print("✅ GuardedDict works\n")

# Test GuardedEnum
print("Testing GuardedEnum...")
class Status(GuardedEnum):
    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"

s1 = Status("active")
assert s1.name == "ACTIVE"
assert s1.value == "active"
print(f"  Status('active') = {s1}, name={s1.name}, value={s1.value}")

s2 = Status("PENDING")
assert s2.name == "PENDING"
print(f"  Status('PENDING') = {s2}, name={s2.name}, value={s2.value}")
print("✅ GuardedEnum works\n")

print("=" * 50)
print("🎉 ALL TESTS PASSED!")
print("=" * 50)
