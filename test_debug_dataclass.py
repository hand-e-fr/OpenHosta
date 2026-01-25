"""Debug test pour guarded_dataclass."""
import sys
sys.path.insert(0, '/home/ebatt/VSCode_GitRepos/OpenHosta.git/src')

from OpenHosta.guarded.subclassablecollections import guarded_dataclass
from OpenHosta.guarded.resolver import TypeResolver

print("Test de TypeResolver:")
print(f"TypeResolver.resolve(int) = {TypeResolver.resolve(int)}")
print(f"TypeResolver.resolve(str) = {TypeResolver.resolve(str)}")

from OpenHosta.guarded import GuardedInt
print(f"\nGuardedInt('25') = {GuardedInt('25')}")

print("\n" + "="*50)
print("Test guarded_dataclass avec debug:")

@guarded_dataclass
class Person:
    name: str
    age: int

print(f"Person class created: {Person}")
print(f"Person.__mro__ = {Person.__mro__}")

# Test avec dict
data = {"name": "Bob", "age": "25"}
print(f"\nTrying Person({data})")

try:
    p = Person(data)
    print(f"✅ Success: {p}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
