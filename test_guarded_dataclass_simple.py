"""Test simple pour guarded_dataclass sans @dataclass."""
import sys
sys.path.insert(0, '/home/ebatt/VSCode_GitRepos/OpenHosta.git/src')

from OpenHosta.guarded import guarded_dataclass

print("Test 1: Usage simple (sans @dataclass explicite)")
@guarded_dataclass
class Person:
    name: str
    age: int

# Test mode kwargs
p1 = Person(name="Alice", age=30)
print(f"✅ Person(name='Alice', age=30)")
print(f"   {p1}")
print(f"   name={p1.name}, age={p1.age}")
print(f"   uncertainty={p1.uncertainty}, level={p1.abstraction_level}")

# Test mode dict - avec conversion de type
print("\nTest 2: Mode dict avec conversion")
try:
    p2 = Person({"name": "Bob", "age": "25"})
    print(f"✅ Person({{'name': 'Bob', 'age': '25'}})")
    print(f"   {p2}")
    print(f"   name={p2.name}, age={p2.age}, type(age)={type(p2.age)}")
    print(f"   uncertainty={p2.uncertainty}, level={p2.abstraction_level}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nTest 3: Avec options dataclass")
@guarded_dataclass(frozen=True)
class Point:
    x: int
    y: int

pt = Point(x=10, y=20)
print(f"✅ Point(x=10, y=20) = {pt}")

# Vérifier frozen
try:
    pt.x = 100
    print("❌ frozen=True n'a pas fonctionné")
except Exception:
    print("✅ frozen=True fonctionne")

print("\nTest 4: Avec valeurs par défaut")
@guarded_dataclass
class Config:
    host: str = "localhost"
    port: int = 8080

c = Config()
print(f"✅ Config() = {c}")
print(f"   host={c.host}, port={c.port}")

print("\n" + "="*50)
print("Tests terminés")
print("="*50)
