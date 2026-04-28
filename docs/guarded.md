# 📖 OpenHosta.guarded Documentation

**OpenHosta.guarded** is the type validation and conversion module with configurable tolerance. It transforms arbitrary inputs into native Python types with confidence and traceability metadata.

---

## I. Introduction: Guarded Types

### Multiple Inheritance Order and MRO

⚠️ **Important rule**: When a Guarded type uses multiple inheritance, `GuardedPrimitive` must be placed **first** in the explicit base class list.

This rule is now **checked at class definition time**: a poorly declared subclass explicitly raises a `TypeError`.

```python
from OpenHosta.guarded.primitives import GuardedPrimitive, ProxyWrapper

class MyGuardedProxy(GuardedPrimitive, ProxyWrapper):
    ...
```

And **not**:

```python
from OpenHosta.guarded.primitives import GuardedPrimitive, ProxyWrapper

class BadProxyOrder(ProxyWrapper, GuardedPrimitive):
    ...
```

Why:
- `GuardedPrimitive.__new__()` drives the entire parsing pipeline (`attempt`, conversion, metadata)
- Other bases may define their own construction logic or interfere with `super()`/the MRO
- `ProxyWrapper` is a **delegation mixin**, not a construction base
- If the order is reversed, the MRO can short-circuit the Guarded pipeline

This rule applies to all multiple-inheritance subclasses, notably proxy types (`GuardedBool`, `GuardedNone`, `GuardedRange`, `GuardedEnum`, etc.).


Guarded types are enriched Python types that:
1. **Accept imperfect inputs** and clean them automatically
2. **Retain metadata** about the conversion quality
3. **Behave like native types** for seamless integration

```python
from OpenHosta.guarded import GuardedInt

# Accepts multiple formats
age = GuardedInt("42")        # Numeric string
price = GuardedInt("1,000")   # With thousands separator
count = GuardedInt(42.0)      # Round float

# Behaves like an int
total = age + 10  # 52

# But retains metadata
print(age.uncertainty)        # 0.0 (perfectly certain)
print(age.abstraction_level)  # 'native'
print(price.uncertainty)      # 0.15 (heuristic parsing)
```

---

## II. Architecture: The Validation Pipeline

Each Guarded type uses a cascading pipeline to convert inputs:

### 2.1 The 4 Parsing Levels

```
Input → Native → Heuristic → Semantic → Knowledge → Output
         ↓        ↓           ↓          ↓
         0.00     0.0-0.15    0.0-0.30   0.0+
         (STRICT) (PRECISE)   (FLEXIBLE) (CREATIVE)
```

1. **Native** (Cost: O(1), Uncertainty: 0.0)
   - Direct type check (`isinstance`)
   - If the value is already the correct type, immediate validation

2. **Heuristic** (Cost: O(n), Uncertainty: 0.05-0.15)
   - Deterministic cleanup (regex, strip, cast)
   - Removal of spaces, separators, currencies
   - Standard format conversion

3. **Semantic** (Cost: ~1s, Uncertainty: 0.15-0.30)
   - LLM-based conversion (not currently implemented)
   - Context and intent comprehension

4. **Knowledge** (Cost: Variable, Uncertainty: 0.30+)
   - Knowledge base lookup
   - Synonym and variant mapping

### 2.2 Tolerance and Control

Tolerance defines how far the pipeline can go.

The constructor always uses the class default tolerance (`_tolerance`).

To force a tolerance, use `attempt()`:

```python
from OpenHosta.guarded import GuardedInt, Tolerance

# Strict tolerance: only the Native level is accepted
strict_result = GuardedInt.attempt("42", tolerance=Tolerance.STRICT)

# Flexible tolerance: Native + Heuristic accepted
flexible_result = GuardedInt.attempt("1,000", tolerance=Tolerance.FLEXIBLE)

# Default tolerance: class _tolerance
value = GuardedInt("1,000")
```

To permanently change the tolerance, create a subclass:

```python
from OpenHosta.guarded import GuardedInt, Tolerance

class StrictGuardedInt(GuardedInt):
    _tolerance = Tolerance.STRICT

value = StrictGuardedInt(42)
```

| Level | Constant | Value | Accepted Levels |
|-------|----------|-------|-----------------|
| **Strict** | `Tolerance.STRICT` | 0.00 | Native only |
| **Precise** | `Tolerance.PRECISE` | 0.05 | Native |
| **Flexible** | `Tolerance.FLEXIBLE` | 0.15 | Native + Heuristic |
| **Type Compliant** | `Tolerance.TYPE_COMPLIANT` | 0.999 | All (default) |

### 2.3 Multi-parameter Constructors

Child classes of `GuardedPrimitive` can now accept multiple positional and keyword arguments.

- If the constructor receives **a single positional argument** and **no kwargs**, the pipeline receives that value directly.
- Otherwise, the inputs are wrapped in a `GuardedCallInput(args, kwargs)` object and passed as a **single value** to the pipeline.

This allows a subclass to implement its own logic in `_parse_native()`, `_parse_heuristic()`, etc., while preserving the current architecture centered on a single `value` input.

```python
from OpenHosta.guarded.primitives import GuardedPrimitive, GuardedCallInput
from OpenHosta.guarded import Tolerance

class FullName(GuardedPrimitive, str):
    _type_en = "a full name"
    _type_py = str
    _tolerance = Tolerance.TYPE_COMPLIANT

    @classmethod
    def _parse_heuristic(cls, value):
        if isinstance(value, GuardedCallInput):
            first = value.kwargs.get("first") or value.args[0]
            last = value.kwargs.get("last") or value.args[1]
            return Tolerance.PRECISE, f"{first.strip()} {last.strip()}", None
        return super()._parse_heuristic(value)

name = FullName("Ada", "Lovelace")
name2 = FullName(first="Ada", last="Lovelace")
```

---

## III. Scalar Types

### 3.1 GuardedInt

Integer with smart parsing.

```python
from OpenHosta.guarded import GuardedInt

# Accepted formats
GuardedInt(42)           # Native int
GuardedInt("42")         # Numeric string
GuardedInt("1,000")      # Thousands separator
GuardedInt("1 000")      # Spaces
GuardedInt("-42")        # Negatives
GuardedInt(42.0)         # Round float
```

**Heuristic Parsing**:
- Space removal
- Comma removal (if no decimal point)
- Regex validation: `-?\d+`

### 3.2 GuardedFloat

Floating-point number with flexible parsing.

```python
from OpenHosta.guarded import GuardedFloat

# Accepted formats
GuardedFloat(3.14)       # Native float
GuardedFloat("3.14")     # String
GuardedFloat("3,14")     # European format
GuardedFloat("1.000,5")  # Thousands + decimals
GuardedFloat(42)         # Int to float
```

**Heuristic Parsing**:
- Replacement `,` → `.` for European format
- Multiple thousands separator handling
- Automatic int → float conversion

### 3.3 GuardedUtf8

String with encoding handling.

```python
from OpenHosta.guarded import GuardedUtf8

# Accepted formats
GuardedUtf8("hello")     # Native string
GuardedUtf8(b"hello")    # UTF-8 bytes
```

**Heuristic Parsing**:
- Automatic bytes → string decoding
- Encoding error handling

---

## III.b Advanced Scalar Types

### 3.4 GuardedComplex

Complex number with smart parsing.

```python
from OpenHosta.guarded import GuardedComplex

# Accepted formats
GuardedComplex(1+2j)         # Native complex
GuardedComplex("1+2j")       # Standard string
GuardedComplex("1 + 2j")     # With spaces
```

### 3.5 GuardedBytes and GuardedByteArray

Binary types with flexible parsing from strings.

```python
from OpenHosta.guarded import GuardedBytes

# Accepted formats
GuardedBytes(b"hello")       # Native bytes
GuardedBytes("hello")        # String (encoded as UTF-8)
GuardedBytes([104, 101])     # List of integers
```

---

## IV. Proxy Types (Non-Subclassable)

Certain Python types cannot be subclassed (`bool`, `NoneType`, etc.). For these, we use a **ProxyWrapper**.

### 4.1 GuardedBool

Boolean with natural language parsing.

```python
from OpenHosta.guarded import GuardedBool

# Accepted formats
b = GuardedBool(True)    # Native bool
b = GuardedBool("yes")   # English
b = GuardedBool("oui")   # French
b = GuardedBool("1")     # Numeric

# Retrieve the native value
b.unwrap()  # → True (real Python bool)

# Comparison
if b:  # Works thanks to __bool__
    print("True")
```

**Knowledge base**:
- True: `["yes", "y", "true", "1", "oui", "vrai", "ok"]`
- False: `["no", "n", "false", "0", "non", "faux"]`

### 4.2 GuardedNone

None type with flexible parsing.

```python
from OpenHosta.guarded import GuardedNone

# Accepted formats
n = GuardedNone(None)      # Native None
n = GuardedNone("None")    # String "None"
n = GuardedNone("null")    # JSON null
n = GuardedNone("nothing") # Natural language

n.unwrap()  # → None
```

### 4.3 Other Proxies (Any, Range, MemoryView)

* **GuardedAny**: Accepts any type, useful as a "pass-through" with metadata.
* **GuardedRange**: Proxy for `range()`. Accepts `range(10)` or string `"0:10"`.
* **GuardedMemoryView**: Proxy for `memoryview`.

### 4.4 ProxyWrapper Behavior

`ProxyWrapper` is now a **mixin**:
- It delegates operations to `_python_value`
- It provides a **recursive** `unwrap()`
- It must not implement the main construction logic
- Construction must be handled by `GuardedPrimitive` via the MRO

⚠️ **Important**: Proxy types are NOT instances of the native type.

```python
from OpenHosta.guarded import GuardedBool

b = GuardedBool("yes")

isinstance(b, bool)        # ❌ False (it's a proxy)
isinstance(b.unwrap(), bool)  # ✅ True

# But they behave like the native type
if b:  # ✅ Works
    pass

b == True  # ✅ True (thanks to __eq__)
```

---

## V. Collections

### 5.1 GuardedList

List with string parsing.

```python
from OpenHosta.guarded import GuardedList

# Accepted formats
lst = GuardedList([1, 2, 3])      # Native list
lst = GuardedList((1, 2, 3))      # Tuple → list
lst = GuardedList({1, 2, 3})      # Set → list
lst = GuardedList("[1, 2, 3]")    # JSON string

# Normal operations
lst.append(4)
lst[0]  # 1
len(lst)  # 4
```

### 5.2 GuardedDict

Dictionary with JSON parsing.

```python
from OpenHosta.guarded import GuardedDict

# Accepted formats
d = GuardedDict({"a": 1})         # Native dict
d = GuardedDict('{"a": 1}')       # JSON string
d = GuardedDict("{'a': 1}")       # Python repr

# Normal operations
d["b"] = 2
d.get("c")  # None
```

### 5.3 GuardedSet and GuardedTuple

Same logic as GuardedList with their respective specificities.

### 5.4 Advanced Composite Types

#### GuardedLiteral

Creates a type restricted to a set of values, similar to `typing.Literal`.

```python
from OpenHosta.guarded import guarded_literal

Color = guarded_literal("red", "green", "blue")

c = Color("red")      # OK
c = Color("RED")      # OK (heuristic: case-insensitive)

# doc-test: raises ValueError
c = Color("yellow")   # Error (outside allowed values)
```

#### GuardedUnion

Creates a type that tries multiple successive conversions, similar to `typing.Union`.

```python
from OpenHosta.guarded import GuardedUnion, guarded_union
from OpenHosta.guarded import GuardedInt, GuardedUtf8

# Tries Int first, otherwise String
IntOrStr = guarded_union(GuardedInt, GuardedUtf8)

v1 = IntOrStr("42")      # → 42 (int)
v2 = IntOrStr("hello")   # → "hello" (str)
```

---

## VI. GuardedEnum: Validated Enums

Create enums with case-insensitive and value-based parsing.

```python
from OpenHosta.guarded import GuardedEnum

class Status(GuardedEnum):
    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"

# Flexible parsing
s1 = Status("active")    # By value
s2 = Status("ACTIVE")    # By name (uppercase)
s3 = Status("pending")   # By value
s4 = Status("Status.ACTIVE")  # EnumName.MEMBER format
s5 = Status(".ACTIVE")        # Short format (.MEMBER)

# enum.Enum compatible API
s1.name   # "ACTIVE"
s1.value  # "active"
repr(s1)  # "<Status.ACTIVE: 'active'>"

# Comparison
s1 == s2  # True
s1 == "ACTIVE"  # True

# Round-trip with repr()
s = Status("ACTIVE")
s_copy = Status(repr(s))  # ✅ Works!
```

**Accepted formats**:
- ✅ By name: `Status("ACTIVE")`
- ✅ By value: `Status("active")`, `Status("pending")`
- ✅ Qualified format: `Status("Status.ACTIVE")`
- ✅ Short format: `Status(".ACTIVE")`
- ✅ Full representation: `Status("<Status.ACTIVE: 'active'>")`

**Advantages**:
- ✅ Case-insensitive parsing
- ✅ Name or value lookup
- ✅ Compatible with `repr()` for serialization/deserialization
- ✅ `enum.Enum` compatible API
- ✅ Confidence metadata

---

## VII. Guarded Dataclasses

Transform your classes into validated dataclasses with a single decorator.

> **Note**: `@guarded_dataclass` automatically applies `@dataclass`, you don't need both!

### 7.1 Simple Usage (Recommended)

```python
from OpenHosta.guarded import guarded_dataclass

@guarded_dataclass
class Person:
    name: str
    age: int

# Standard creation with kwargs
p1 = Person(name="Alice", age=30)

# Standard creation with positional args
p1b = Person("Alice", 30)

# Creation from dict with automatic conversion
p2 = Person({"name": "Bob", "age": "25"})  # age converted from str → int

# Fields are validated and converted
assert p2.age == 25
assert isinstance(p2.age, int)  # Automatically converted
```

### 7.2 Args and kwargs in Guarded Dataclasses

Classes decorated with `@guarded_dataclass` now support:

- Classic **kwargs**
- **Positional args**
- Inputs as **dict**
- Text representations in constructor or dictionary format

```python
from OpenHosta.guarded import guarded_dataclass

@guarded_dataclass
class Point:
    x: int
    y: int

p1 = Point(10, 20)
p2 = Point(x=10, y=20)
p3 = Point({"x": "10", "y": "20"})
p4 = Point("Point(x=10, y=20)")
```

Internally, if multiple arguments are provided to the constructor, they are wrapped as `GuardedCallInput(args, kwargs)` then parsed by the pipeline.

### 7.3 With Dataclass Options

You can pass options directly to `@guarded_dataclass`:

```python
from OpenHosta.guarded import guarded_dataclass

@guarded_dataclass(frozen=True, order=True)
class Point:
    x: int
    y: int

pt = Point(x=10, y=20)
# pt.x = 100  # ❌ Error: frozen=True
```

### 7.4 With Default Values

```python
from OpenHosta.guarded import guarded_dataclass

@guarded_dataclass
class Config:
    host: str = "localhost"
    port: int = 8080
    debug: bool = False

# Use defaults
c1 = Config()
assert c1.host == "localhost"

# Partial override
c2 = Config(host="example.com")
assert c2.port == 8080  # Keeps default value

# From dict
c3 = Config({"host": "api.example.com", "port": "3000"})
assert c3.port == 3000  # Converted from "3000" (str) → 3000 (int)
```

### 7.5 Automatic Type Conversion

The decorator uses `TypeResolver` to automatically convert values:

```python
from OpenHosta.guarded import guarded_dataclass

@guarded_dataclass
class User:
    username: str
    age: int
    active: bool
    tags: list

# All conversions are automatic
user = User({
    "username": "alice",
    "age": "25",        # str → int
    "active": "yes",    # str → bool
    "tags": "python,ai" # str → list (CSV parsing)
})

assert user.age == 25
assert user.active == True
assert isinstance(user.tags, list)
```

### 7.6 Guarded Metadata

Like all Guarded types, dataclasses retain metadata:

```python
from OpenHosta.guarded import guarded_dataclass

@guarded_dataclass
class Product:
    name: str
    price: float

# Creation from dict
p = Product({"name": "Widget", "price": "9.99"})

# Metadata available
print(p.uncertainty)        # 0.15 (FLEXIBLE - heuristic parsing)
print(p.abstraction_level)  # 'heuristic'

# Normal creation
p2 = Product(name="Gadget", price=19.99)
print(p2.uncertainty)       # 0.0 (STRICT - native values)
print(p2.abstraction_level) # 'native'
```

### 7.7 Legacy Usage (With Explicit @dataclass)

If you already have `@dataclass`, `@guarded_dataclass` detects it and won't reapply it:

```python
from dataclasses import dataclass
from OpenHosta.guarded import guarded_dataclass

@guarded_dataclass
@dataclass
class Person:
    name: str
    age: int

# Works exactly the same
```

> **Recommendation**: Use only `@guarded_dataclass` for cleaner code.

---

## VIII. TypeResolver: Automatic Resolution

The `TypeResolver` converts Python annotations into Guarded types.

```python
from typing import List, Dict, Optional
from OpenHosta.guarded.resolver import TypeResolver, type_returned_data

# Simple type resolution
TypeResolver.resolve(int)    # → GuardedInt
TypeResolver.resolve(str)    # → GuardedUtf8
TypeResolver.resolve(bool)   # → GuardedBool

# Complex type resolution
TypeResolver.resolve(List[int])        # → GuardedList
TypeResolver.resolve(Dict[str, int])   # → GuardedDict
TypeResolver.resolve(Optional[int])    # → GuardedInt

# Usage in the pipeline
result = type_returned_data("42", int)  # Converts "42" → 42
```

**Used by**: The OpenHosta pipeline to automatically type LLM responses.

---

## IX. Creating Your Own Types

Inherit from `GuardedPrimitive` to create custom business types.

### 9.1 Complete Example: CorporateEmail with 4-Level Pipeline

This example shows **all pipeline levels** with LLM validation and a corporate directory.

```python
import re
from typing import Tuple, Optional, Any
from OpenHosta.guarded import GuardedUtf8, Tolerance
from OpenHosta.guarded.primitives import UncertaintyLevel
from OpenHosta import emulate

# Corporate directory (simulated)
CORPORATE_DIRECTORY = {
    "marie.dupont@mycorp.com",
    "jean.martin@mycorp.com",
    "sophie.bernard@mycorp.com",
    "pierre.dubois@mycorp.com",
}

class CorporateEmail(GuardedUtf8):
    """Corporate email validated against the mycorp.com directory"""
    
    _type_en = (
        "a corporate email address in the format firstname.lastname@mycorp.com "
        "where firstname and lastname are lowercase letters only"
    )
    _type_py = str
    _type_json = {
        "type": "string",
        "format": "email",
        "pattern": r"^[a-z]+\.[a-z]+@mycorp\.com$"
    }
    _type_knowledge = {
        "directory": CORPORATE_DIRECTORY,
        "domain": "mycorp.com"
    }
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """Level 1: Perfect email in the directory (0.00 - STRICT)."""
        if not isinstance(value, str):
            return UncertaintyLevel(Tolerance.ANYTHING), value, "Not a string"
        
        # NO cleanup - only accept perfect emails
        if not re.match(r"^[a-z]+\.[a-z]+@mycorp\.com$", value):
            return UncertaintyLevel(Tolerance.ANYTHING), value, "Invalid format"
        
        if value in cls._type_knowledge["directory"]:
            return UncertaintyLevel(Tolerance.STRICT), value, None
        
        return UncertaintyLevel(Tolerance.ANYTHING), value, "Not in directory"
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """Level 2: Deterministic cleanup (0.05 - PRECISE)."""
        if not isinstance(value, str):
            return UncertaintyLevel(Tolerance.ANYTHING), value, "Not a string"
        
        original = value
        cleaned = value.strip().lower()
        cleaned = cleaned.replace("mailto:", "").replace("<", "").replace(">", "")
        cleaned = cleaned.replace(" ", "").replace("\t", "")
        
        # Check format after cleanup
        if re.match(r"^[a-z]+\.[a-z]+@mycorp\.com$", cleaned):
            if cleaned in cls._type_knowledge["directory"]:
                # Cleanup performed and in directory → PRECISE
                if cleaned != original:
                    return UncertaintyLevel(Tolerance.PRECISE), cleaned, None
                # No cleanup but in directory (already handled by native, but for robustness)
                return UncertaintyLevel(Tolerance.STRICT), cleaned, None
            else:
                # Valid format but not in directory → FLEXIBLE
                return UncertaintyLevel(Tolerance.FLEXIBLE), cleaned, "Valid format, not in directory"
        
        return UncertaintyLevel(Tolerance.ANYTHING), value, "Invalid format after heuristic cleaning"
    
    @classmethod
    def _llm_cast_email(cls, text: str) -> str | None:
        """
        Convert the input text to a valid corporate email: firstname.lastname@mycorp.com
        
        Rules:
        - Only lowercase letters for firstname and lastname
        - Examples:
            * "marie dot dupont at mycorp dor com" → "marie.dupont@mycorp.com"
            * "jean martin mycorp" → "jean.martin@mycorp.com"
        
        If the input cannot be converted, return None.
        """
        return emulate()

    @classmethod
    def _parse_semantic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """Level 3: LLM correction (0.15 - FLEXIBLE)."""
        if not isinstance(value, str):
            return UncertaintyLevel(Tolerance.ANYTHING), value, "Not a string"
        
        corrected = cls._llm_cast_email(value)
        
        if corrected and re.match(r"^[a-z]+\.[a-z]+@mycorp\.com$", corrected):
            # Corrected email exists in directory → FLEXIBLE
            if corrected in cls._type_knowledge["directory"]:
                return UncertaintyLevel(Tolerance.FLEXIBLE), corrected, None
            
            # Otherwise, pass to knowledge level
            return UncertaintyLevel(Tolerance.ANYTHING), corrected, "LLM corrected but not in directory"
        
        return UncertaintyLevel(Tolerance.ANYTHING), value, "Cannot parse semantically"
    
    @classmethod
    def _parse_knowledge(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """Level 4: Fuzzy matching (0.30 - CREATIVE)."""
        if not isinstance(value, str):
            return UncertaintyLevel(Tolerance.ANYTHING), value, "Not a string"
        
        # Try to normalize the input for fuzzy matching
        cleaned = value.strip().lower()
        cleaned = cleaned.replace("mailto:", "").replace("<", "").replace(">", "")
        cleaned = cleaned.replace(" ", "").replace("\t", "")
        
        # Extract first and last name if the format is close
        match = re.match(r"^([a-z]+)\.?([a-z]+)?@?([a-z\.]*)?$", cleaned)
        if not match:
            return UncertaintyLevel(Tolerance.ANYTHING), value, "Cannot extract name parts for fuzzy matching"
        
        firstname_raw, lastname_raw, domain_raw = match.groups()
        
        # If the domain is present and incorrect, we can't fuzzy match
        if domain_raw and not domain_raw.startswith(cls._type_knowledge["domain"].split('.')[0]):
             return UncertaintyLevel(Tolerance.ANYTHING), value, "Incorrect domain for fuzzy matching"

        # Try to find the best match in the directory
        best_match = cls._find_closest_email(firstname_raw, lastname_raw)
        
        if best_match:
            return UncertaintyLevel(Tolerance.CREATIVE), best_match, "Fuzzy matched to directory"
        
        return UncertaintyLevel(Tolerance.ANYTHING), value, "No fuzzy match found in directory"
    
    @classmethod
    def _find_closest_email(cls, firstname: str, lastname: str) -> Optional[str]:
        """Find the closest email by Levenshtein distance."""
        from difflib import get_close_matches
        
        directory_names = []
        for email in cls._type_knowledge["directory"]:
            m = re.match(r"^([a-z]+)\.([a-z]+)@", email)
            if m:
                directory_names.append((m.group(1), m.group(2), email))
        
        # Find close first names
        firstnames_in_dir = [n[0] for n in directory_names]
        close_first = get_close_matches(firstname, firstnames_in_dir, n=1, cutoff=0.7)
        if not close_first:
            return None
        
        # Filter candidates by close first name
        candidates_for_lastname = [(n[1], n[2]) for n in directory_names if n[0] == close_first[0]]
        if not candidates_for_lastname:
            return None
            
        lastnames_in_candidates = [c[0] for c in candidates_for_lastname]
        close_last = get_close_matches(lastname, lastnames_in_candidates, n=1, cutoff=0.7)
        
        if close_last:
            for cand_last, email in candidates_for_lastname:
                if cand_last == close_last[0]:
                    return email
        return None


# ============================================================================
# DEMONSTRATION
# ============================================================================

# NATIVE level (0.00)
email1 = CorporateEmail("marie.dupont@mycorp.com")
print(f"{email1} - {email1.abstraction_level} - {email1.uncertainty}")
# → marie.dupont@mycorp.com - native - 0.0

# HEURISTIC level (0.05)
email2 = CorporateEmail("  MARIE.DUPONT@MYCORP.COM  ")
print(f"{email2} - {email2.abstraction_level} - {email2.uncertainty}")
# → marie.dupont@mycorp.com - heuristic - 0.05

# SEMANTIC level (0.15) - LLM Correction
email3 = CorporateEmail("marie dot dupont at mycorp dor com")
print(f"{email3} - {email3.abstraction_level} - {email3.uncertainty}")
# → marie.dupont@mycorp.com - semantic - 0.15

# KNOWLEDGE level (0.30) - Fuzzy matching
email4 = CorporateEmail("m.dupond@mycorp.com")  # dupond -> dupont
print(f"{email4} - {email4.abstraction_level} - {email4.uncertainty}")
# → marie.dupont@mycorp.com - knowledge - 0.30

# HEURISTIC with valid format but not in directory (0.10)
email5 = CorporateEmail("john.doe@mycorp.com")  # Valid format, but not in CORPORATE_DIRECTORY
print(f"{email5} - {email5.abstraction_level} - {email5.uncertainty}")
# → john.doe@mycorp.com - heuristic - 0.10

# Confidence-based decision
if email3.uncertainty <= Tolerance.PRECISE:
    print("✅ Automatic validation")
elif email3.uncertainty <= Tolerance.FLEXIBLE:
    print("⚠️  Ask for confirmation")  # ← This case
else:
    print("❌ Reject")
```

**Key points**:

1. **`_parse_native`**: No cleanup, strict validation only
2. **`_parse_heuristic`**: Detects if cleanup was performed (`cleaned != original`)
3. **`_parse_semantic`**: Uses `closure()` for real LLM call
4. **`_parse_knowledge`**: Fuzzy matching with `difflib.get_close_matches()`
5. **Directory validation**: If corrected email exists → FLEXIBLE confidence, otherwise passes to next level

**Complete tests**: See [`tests/guarded/test_corporate_email.py`](https://github.com/hand-e-fr/OpenHosta/blob/main/tests/guarded/test_corporate_email.py) (13/13 tests pass ✅)

### 9.2 Methods to Implement

| Method | Required | Description |
|--------|----------|-------------|
| `_parse_native` | ✅ Yes | Strict type validation |
| `_parse_heuristic` | ⚠️ Recommended | Deterministic cleanup |
| `_parse_semantic` | ❌ No | LLM-based conversion |
| `_parse_knowledge` | ❌ No | Knowledge base |

### 9.3 Configuration Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `_type_en` | `str` | English description for the LLM |
| `_type_py` | `type` | Target Python type |
| `_type_json` | `dict` | JSON Schema for validation |
| `_type_knowledge` | `dict\|Any` | Knowledge base (optional) |
| `_tolerance` | `Tolerance` | Default tolerance |

---

## X. Metadata and Traceability

Each Guarded instance retains metadata about its creation.

### 10.1 Available Attributes

```python
from OpenHosta.guarded import GuardedInt

age = GuardedInt("1,000")

# Metadata
age.uncertainty         # 0.15 (confidence level)
age.abstraction_level   # 'heuristic' (method used)
age.unwrap()           # Native value (for ProxyWrapper)

# Normal operations
age + 10   # 1010
age > 500  # True
```

### 10.2 Abstraction Levels

| Level | Description | Typical Uncertainty |
|-------|-------------|---------------------|
| `native` | Value already the correct type | 0.0 |
| `heuristic` | Deterministic cleanup | 0.05-0.15 |
| `semantic` | LLM conversion | 0.15-0.30 |
| `knowledge` | Knowledge base | 0.30+ |

---

## XI. Pydantic Integration

Guarded types integrate with Pydantic V2.

```python
from pydantic import BaseModel
from OpenHosta.guarded import GuardedInt, GuardedUtf8

class User(BaseModel):
    name: GuardedUtf8
    age: GuardedInt

# Pydantic + Guarded = Tolerant validation
user = User(name="Alice", age="25")  # age converted automatically
```

---

## XII. Best Practices

### ✅ Do

1. **Use Guarded types for user inputs**
   ```python
   age = GuardedInt(user_input)  # Tolerant
   ```

2. **Force tolerance via `attempt()` for critical cases**
   ```python
   result = GuardedUtf8.attempt(input, tolerance=Tolerance.STRICT)
   if not result.success:
       raise ValueError(result.error_message)
   password = result.data
   ```

3. **Check uncertainty for important decisions**
   ```python
   amount = GuardedFloat(input)
   if amount.uncertainty > Tolerance.PRECISE:
       logger.warning(f"Uncertain amount: {amount}")
   ```

### ❌ Don't

1. **Don't use as native dict keys**
   ```python
   # ❌ Error: ProxyWrapper types are not hashable
   d = {GuardedBool("yes"): "value"}
   
   # ✅ Use GuardedDict or unwrap()
   d = {GuardedBool("yes").unwrap(): "value"}
   ```

2. **Don't ignore metadata**
   ```python
   # ❌ Ignoring uncertainty
   price = GuardedFloat(dirty_input)
   charge_customer(price)
   
   # ✅ Check confidence
   price = GuardedFloat(dirty_input)
   if price.uncertainty <= Tolerance.PRECISE:
       charge_customer(price)
   else:
       ask_confirmation(price)
   ```

---

## XIII. Comparison with Pydantic

| Aspect | Pydantic | OpenHosta Guarded |
|--------|----------|-------------------|
| **Philosophy** | Strict validation | Tolerant conversion |
| **Input** | Structured data | Anything |
| **Failure** | Raises ValidationError | Attempts to repair |
| **Performance** | ⚡ Very fast | 🐢 Slower (if parsing) |
| **Metadata** | No | Yes (uncertainty, level) |
| **Use case** | APIs, Config | AI agents, Scraping |

**Use Pydantic** to validate technical APIs.  
**Use Guarded** to parse human or LLM inputs.

---

## XIV. Known Limitations

### 14.1 Known Bugs

1. **GuardedList - CSV Parsing**
   - `GuardedList("1,2,3")` converts to a character list
   - **Workaround**: Use JSON format `"[1,2,3]"`

2. **ProxyWrapper - isinstance()**
   - `isinstance(GuardedBool("yes"), bool)` returns `False`
   - **Workaround**: Use `.unwrap()` for the native type

### 14.2 Unimplemented Types

- `GuardedRange` (partial)
- `GuardedMemoryView` (partial)
- `GuardedCode` (Supported since v4.1, see [callables.md](callables.md))
- Semantic parsing (LLM) not connected

---

## XV. Complete Examples

### 15.1 Form Validation

```python
from OpenHosta.guarded import GuardedInt, GuardedUtf8, GuardedBool

# Dirty data from a web form
form_data = {
    "name": "  Alice  ",
    "age": "twenty-five",  # Would require LLM (not implemented)
    "age": "25 years",     # Works with heuristic
    "newsletter": "yes"
}

name = GuardedUtf8(form_data["name"])      # "Alice"
age = GuardedInt(form_data["age"])         # 25
newsletter = GuardedBool(form_data["newsletter"])  # True

print(f"{name}, {age} years old, newsletter: {newsletter.unwrap()}")
```

### 15.2 Configuration Parsing

```python
from OpenHosta.guarded import GuardedInt, GuardedDict

config_str = '{"port": "8080", "debug": "true"}'
config = GuardedDict(config_str)

port = GuardedInt(config["port"])  # 8080
```

---

## XVI. Resources

- **Source code**: `src/OpenHosta/guarded/`
- **Tests**: `tests/guarded/`
- **Examples**: `test_guarded_basic.py`

**Modules**:
- `primitives.py` - Base class `GuardedPrimitive`
- `constants.py` - `Tolerance` enumerations
- `subclassablescalars.py` - Scalar types
- `subclassablewithproxy.py` - Proxy types
- `subclassablecollections.py` - Collections and dataclasses
- `subclassableclasses.py` - GuardedEnum
- `resolver.py` - Type resolution

---

## X. Direct Usage: Parsing LLM Output

While OpenHosta usually handles parsing automatically via `emulate()`, you can use Guarded types directly to parse raw strings from any LLM client (OpenAI, Anthropic, LangChain, etc.).

### 10.1 Using TypeResolver

The most robust way to parse a string into a specific type is to use `TypeResolver.resolve()`. It handles all Python annotations (List, Dict, Dataclasses, etc.).

```python
from typing import List
from OpenHosta.guarded.resolver import TypeResolver

# 1. Define your expected type
MyType = List[int]

# 2. Get the LLM output (raw string)
raw_output = "I found these numbers: [10, 20, 30] # and some noise"

# 3. Resolve the type and parse
guarded_type = TypeResolver.resolve(MyType)
result = guarded_type.attempt(raw_output)

if result.success:
    data = result.data  # [10, 20, 30]
    print(f"Parsed {len(data)} items with uncertainty {result.uncertainty}")
else:
    print(f"Parsing failed: {result.error_message}")
```

### 10.2 Integrating with a custom Model call

If you are using an OpenHosta `Model` instance directly:

```python
from OpenHosta.defaults import config
from OpenHosta.guarded.resolver import TypeResolver

model = config.DefaultModel
messages = [{"role": "user", "content": "Return the price of BTC as a float."}]

# Call the LLM
response_dict = model.api_call(messages)
raw_content = model.get_response_content(response_dict)

# Parse directly
price = TypeResolver.resolve(float).attempt(raw_content).data

print(f"Current price: {price}")
```

### 10.3 Why use `attempt()`?

Using `attempt()` instead of direct instantiation (e.g., `GuardedInt(val)`) gives you more control:

1. **No Exceptions**: It returns a `CastingResult` instead of raising `ValueError`, making it safer for production pipelines.
2. **Metadata**: You get the `uncertainty` and `abstraction_level` (native vs heuristic).
3. **Configurable Tolerance**: You can specify how "creative" the parser should be.

```python
from OpenHosta.guarded import GuardedInt, Tolerance

result = GuardedInt.attempt("42 # with comments", tolerance=Tolerance.STRICT)
# result.success will be False (STRICT only accepts clean "42")

result = GuardedInt.attempt("42 # with comments", tolerance=Tolerance.FLEXIBLE)
# result.success will be True (FLEXIBLE accepts heuristic cleaning)
```
