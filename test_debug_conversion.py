"""Debug pour comprendre le problème de conversion."""
import sys
sys.path.insert(0, '/home/ebatt/VSCode_GitRepos/OpenHosta.git/src')

from OpenHosta.guarded import guarded_dataclass, GuardedInt
from OpenHosta.guarded.resolver import TypeResolver
from dataclasses import fields

@guarded_dataclass
class Person:
    name: str
    age: int

print("Test de conversion manuelle:")
print(f"TypeResolver.resolve(int) = {TypeResolver.resolve(int)}")
print(f"TypeResolver.resolve(str) = {TypeResolver.resolve(str)}")

GuardedIntType = TypeResolver.resolve(int)
print(f"\nGuardedIntType = {GuardedIntType}")
print(f"GuardedIntType('25') = {GuardedIntType('25')}")
print(f"type(GuardedIntType('25')) = {type(GuardedIntType('25'))}")

print("\nFields de Person:")
for field in fields(Person):
    print(f"  {field.name}: {field.type}")

print("\nTest de conversion dans le contexte:")
data = {"name": "Bob", "age": "25"}
field_values = {}

for field in fields(Person):
    if field.name in data:
        value = data[field.name]
        print(f"\nField: {field.name}, type: {field.type}, value: {value!r}")
        
        if field.type and value is not None:
            try:
                guarded_type = TypeResolver.resolve(field.type)
                print(f"  Resolved to: {guarded_type}")
                
                if hasattr(guarded_type, '__new__'):
                    converted = guarded_type(value)
                    print(f"  Converted: {converted!r}, type: {type(converted)}")
                    value = converted
            except Exception as e:
                print(f"  ❌ Exception: {e}")
                import traceback
                traceback.print_exc()
        
        field_values[field.name] = value

print(f"\nfield_values = {field_values}")
print(f"Types: name={type(field_values['name'])}, age={type(field_values['age'])}")

print("\nEssai de création:")
try:
    p = Person(**field_values)
    print(f"✅ Success: {p}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
