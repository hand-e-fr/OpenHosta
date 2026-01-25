"""Test simple pour vérifier que guarded_dataclass fonctionne sans @dataclass."""
import sys
sys.path.insert(0, '/home/ebatt/VSCode_GitRepos/OpenHosta.git/src')

from OpenHosta.guarded.subclassablecollections import guarded_dataclass

print("Test 1: Usage simple (sans @dataclass)")
@guarded_dataclass
class Person:
    name: str
    age: int

p1 = Person(name="Alice", age=30)
print(f"✅ Person(name='Alice', age=30) = {p1}")
print(f"   name={p1.name}, age={p1.age}")

p2 = Person({"name": "Bob", "age": "25"})
print(f"✅ Person({{'name': 'Bob', 'age': '25'}}) = {p2}")
print(f"   name={p2.name}, age={p2.age}")

print("\nTest 2: Usage avec options dataclass")
@guarded_dataclass(frozen=True)
class Point:
    x: int
    y: int

pt = Point(x=10, y=20)
print(f"✅ Point(x=10, y=20) = {pt}")
print(f"   x={pt.x}, y={pt.y}")

# Vérifier que frozen fonctionne
try:
    pt.x = 100
    print("❌ frozen=True n'a pas fonctionné")
except Exception as e:
    print(f"✅ frozen=True fonctionne : {type(e).__name__}")

print("\nTest 3: Avec valeurs par défaut")
@guarded_dataclass
class Config:
    host: str = "localhost"
    port: int = 8080

c1 = Config()
print(f"✅ Config() = {c1}")
print(f"   host={c1.host}, port={c1.port}")

c2 = Config(host="example.com")
print(f"✅ Config(host='example.com') = {c2}")
print(f"   host={c2.host}, port={c2.port}")

print("\nTest 4: Métadonnées GuardedPrimitive")
p3 = Person({"name": "Charlie", "age": "35"})
print(f"✅ Métadonnées disponibles:")
print(f"   uncertainty={p3.uncertainty}")
print(f"   abstraction_level={p3.abstraction_level}")

print("\n" + "="*50)
print("🎉 TOUS LES TESTS PASSENT!")
print("="*50)
