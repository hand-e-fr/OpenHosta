"""Test pour vérifier si GuardedEnum accepte le format 'EnumName.MEMBER'."""
import sys
sys.path.insert(0, '/home/ebatt/VSCode_GitRepos/OpenHosta.git/src')

from OpenHosta.guarded import GuardedEnum

class Status(GuardedEnum):
    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"

print("Test 1: Par nom simple")
s1 = Status("PENDING")
print(f"✅ Status('PENDING') = {s1}")

print("\nTest 2: Par valeur")
s2 = Status("pending")
print(f"✅ Status('pending') = {s2}")

print("\nTest 3: Format 'EnumName.MEMBER'")
try:
    s3 = Status("Status.PENDING")
    print(f"✅ Status('Status.PENDING') = {s3}")
except Exception as e:
    print(f"❌ Status('Status.PENDING') failed: {e}")

print("\nTest 4: Format avec juste '.MEMBER'")
try:
    s4 = Status(".PENDING")
    print(f"✅ Status('.PENDING') = {s4}")
except Exception as e:
    print(f"❌ Status('.PENDING') failed: {e}")

print("\nTest 5: repr() format")
s5 = Status("ACTIVE")
print(f"repr(Status('ACTIVE')) = {repr(s5)}")
print(f"Devrait accepter: Status('{repr(s5)}')")
try:
    s6 = Status(repr(s5))
    print(f"✅ Status(repr(s5)) = {s6}")
except Exception as e:
    print(f"❌ Status(repr(s5)) failed: {e}")
