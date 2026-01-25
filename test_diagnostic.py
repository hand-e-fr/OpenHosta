"""Simple diagnostic test without pytest."""
import sys
sys.path.insert(0, '/home/ebatt/VSCode_GitRepos/OpenHosta.git/src')

from OpenHosta.guarded.constants import Tolerance
from OpenHosta.guarded.subclassablescalars import GuardedInt

print("Testing GuardedInt tolerance levels...")
print(f"Default tolerance: {GuardedInt._tolerance}")
print(f"STRICT: {Tolerance.STRICT}")
print(f"PRECISE: {Tolerance.PRECISE}")
print(f"FLEXIBLE: {Tolerance.FLEXIBLE}")
print(f"TYPE_COMPLIANT: {Tolerance.TYPE_COMPLIANT}")
print()

# Test 1: Native int
print("Test 1: Native int")
try:
    age = GuardedInt(42)
    print(f"✅ GuardedInt(42) = {age}, uncertainty={age.uncertainty}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Numeric string (native level)
print("\nTest 2: Numeric string")
try:
    age = GuardedInt("42")
    print(f"✅ GuardedInt('42') = {age}, uncertainty={age.uncertainty}, level={age.abstraction_level}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: String with comma (heuristic level)
print("\nTest 3: String with comma")
try:
    age = GuardedInt("1,000")
    print(f"✅ GuardedInt('1,000') = {age}, uncertainty={age.uncertainty}, level={age.abstraction_level}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: With explicit tolerance
print("\nTest 4: With explicit tolerance")
try:
    age = GuardedInt("1,000", tolerance=Tolerance.FLEXIBLE)
    print(f"✅ GuardedInt('1,000', tolerance=FLEXIBLE) = {age}, uncertainty={age.uncertainty}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Check what _parse_heuristic returns
print("\nTest 5: Direct call to _parse_heuristic")
uncertainty, value, message = GuardedInt._parse_heuristic("1,000")
print(f"_parse_heuristic('1,000') returns:")
print(f"  uncertainty: {uncertainty}")
print(f"  value: {value}")
print(f"  message: {message}")
print(f"  uncertainty <= PRECISE? {uncertainty <= Tolerance.PRECISE}")
print(f"  uncertainty <= FLEXIBLE? {uncertainty <= Tolerance.FLEXIBLE}")
