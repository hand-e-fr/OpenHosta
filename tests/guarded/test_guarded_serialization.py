"""
Tests unitaires — Guarded[T] V5 : Miroir Tri-Modal (serialisation)
=================================================================

Couverture :
  - guarded_to_python : functions, dataclass types, enum types, primitive values, Guarded values
  - guarded_to_json  : primitives, enums, dataclass types, None, bool (before int)
  - guarded_to_markdown : dataclass types, enum types, functions
"""

import sys
from pathlib import Path

import dataclasses
from dataclasses import dataclass
from enum import Enum
import pytest

# Importer le module V5 depuis next_v5/
V5_PATH = str(Path(__file__).parent.parent.parent / "next_v5")
sys.path.insert(0, V5_PATH)

from openhosta import (
    Guarded,
    GuardMetadata,
    guarded_to_python,
    guarded_to_json,
    guarded_to_markdown,
)


# --------------------------------------------------------------------------- #
# Fixtures                                                                      #
# --------------------------------------------------------------------------- #

@dataclass
class Address:
    """An address with street, city and zip code."""
    street: str
    city: str
    zip_code: int


@dataclass
class Person:
    """A person with name, age and address."""
    name: str
    age: int
    address: Address


class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


def greet(name: str) -> str:
    """Greet a person by name."""
    return f"Hello, {name}!"


# =================================================================== #
# 1. guarded_to_python tests                                          #
# =================================================================== #

class TestGuardedToPython:
    """Génération de code Python via introspection."""

    # -- Functions --
    def test_to_python_function_signature(self):
        code = guarded_to_python(add)
        assert "def add" in code
        assert "a: int" in code
        assert "b: int" in code
        assert "-> int" in code

    def test_to_python_function_with_docstring(self):
        code = guarded_to_python(greet)
        assert "def greet" in code
        assert "name: str" in code
        assert "Hello, {name}!" in code or "Say hello" in code or "Greet" in code

    def test_to_python_lambda(self):
        fn = lambda x: x + 1  # noqa: E731
        code = guarded_to_python(fn)
        assert "lambda" in code or "<lambda>" in code or "def <lambda>" in code or "def " in code

    # -- Dataclass types --
    def test_to_python_dataclass_type(self):
        code = guarded_to_python(Address)
        assert "@dataclasses.dataclass" in code
        assert "class Address:" in code
        assert "street:" in code
        assert "city:" in code
        assert "zip_code:" in code

    def test_to_python_dataclass_with_docstring(self):
        code = guarded_to_python(Address)
        assert "street, city" in code or "zip code" in code or "An address" in code

    def test_to_python_nested_dataclass(self):
        code = guarded_to_python(Person)
        assert "class Person:" in code
        assert "name:" in code
        assert "age:" in code
        assert "address:" in code

    # -- Enum types --
    def test_to_python_enum_type(self):
        code = guarded_to_python(Color)
        assert "class Color(Enum):" in code
        assert "RED" in code
        assert "GREEN" in code
        assert "BLUE" in code

    def test_to_python_enum_with_values(self):
        code = guarded_to_python(Color)
        assert "RED = 'red'" in code or 'RED = "red"' in code

    def test_to_python_enum_integer(self):
        code = guarded_to_python(Priority)
        assert "class Priority(Enum):" in code
        assert "LOW = 1" in code
        assert "HIGH = 3" in code

    # -- Primitive values --
    def test_to_python_int_value(self):
        code = guarded_to_python(42)
        assert "type: int" in code
        assert "42" in code

    def test_to_python_string_value(self):
        code = guarded_to_python("hello")
        assert "type: str" in code
        assert "'hello'" in code

    def test_to_python_float_value(self):
        code = guarded_to_python(3.14)
        assert "type: float" in code
        assert "3.14" in code

    def test_to_python_bool_value(self):
        code = guarded_to_python(True)
        assert "type: bool" in code
        assert "True" in code

    def test_to_python_none_value(self):
        code = guarded_to_python(None)
        assert "type: NoneType" in code
        assert "None" in code

    # -- Guarded values --
    def test_to_python_guarded_int_value(self):
        g = Guarded(42, GuardMetadata())
        code = guarded_to_python(g)
        assert "type: int" in code
        assert "42" in code

    def test_to_python_guarded_string_value(self):
        g = Guarded("hello", GuardMetadata(uncertainty=0.3))
        code = guarded_to_python(g)
        assert "type: str" in code

    def test_to_python_guarded_dataclass_type(self):
        """guarded_to_python doit dé-guarder avant de traiter."""
        g = Guarded(Address, GuardMetadata())
        code = guarded_to_python(g)
        assert "class Address:" in code
        assert "street:" in code

    def test_to_python_callable_value(self):
        """guarded_to_python sur une fonction lambda."""
        fn = lambda: 42  # noqa: E731
        g = Guarded(fn, GuardMetadata())
        code = guarded_to_python(g)
        # Should contain the function representation
        assert "lambda" in code or "def" in code or "callable" in code.lower() or "{fn" in code or "<" in code


# =================================================================== #
# 2. guarded_to_json tests                                            #
# =================================================================== #

class TestGuardedToJSON:
    """Génération de JSON Schema standard."""

    # -- Primitives --
    def test_to_json_string(self):
        assert guarded_to_json("hello") == {"type": "string"}

    def test_to_json_int(self):
        assert guarded_to_json(42) == {"type": "integer"}

    def test_to_json_float(self):
        assert guarded_to_json(3.14) == {"type": "number"}

    def test_to_json_bool_true(self):
        assert guarded_to_json(True) == {"type": "boolean"}

    def test_to_json_bool_false(self):
        assert guarded_to_json(False) == {"type": "boolean"}

    def test_to_json_null(self):
        assert guarded_to_json(None) == {"type": "null"}

    def test_to_json_bool_not_int(self):
        """Vérifier que bool n'est pas confondu avec int (subclass Python)."""
        result = guarded_to_json(True)
        assert result == {"type": "boolean"}
        assert result != {"type": "integer"}

    # -- Enum types --
    def test_to_json_enum_string(self):
        schema = guarded_to_json(Color)
        assert schema["type"] == "string"
        assert schema["enum"] == ["red", "green", "blue"]
        assert schema["title"] == "Color"

    def test_to_json_enum_int(self):
        schema = guarded_to_json(Priority)
        assert schema["type"] == "integer"
        assert schema["enum"] == [1, 2, 3]
        assert schema["title"] == "Priority"

    # -- Dataclass types --
    def test_to_json_dataclass_object(self):
        schema = guarded_to_json(Address)
        assert schema["type"] == "object"
        assert schema["title"] == "Address"
        assert "properties" in schema
        assert "street" in schema["properties"]
        assert "city" in schema["properties"]
        assert "zip_code" in schema["properties"]

    def test_to_json_dataclass_required(self):
        schema = guarded_to_json(Address)
        assert "required" in schema
        assert "street" in schema["required"]
        assert "city" in schema["required"]
        assert "zip_code" in schema["required"]

    def test_to_json_dataclass_with_description(self):
        schema = guarded_to_json(Address)
        assert "description" in schema
        assert "address" in schema["description"].lower()

    def test_to_json_dataclass_property_types(self):
        schema = guarded_to_json(Address)
        props = schema["properties"]
        assert props["street"]["type"] == "string"
        assert props["city"]["type"] == "string"
        assert props["zip_code"]["type"] == "integer"

    def test_to_json_nested_dataclass(self):
        schema = guarded_to_json(Person)
        assert schema["type"] == "object"
        props = schema["properties"]
        assert "name" in props
        assert "age" in props
        assert "address" in props
        # Nested address should be an object type
        assert props["address"]["type"] == "object"

    # -- Guarded values --
    def test_to_json_guarded_string(self):
        g = Guarded("hello", GuardMetadata())
        schema = guarded_to_json(g)
        assert schema == {"type": "string"}

    def test_to_json_guarded_int(self):
        g = Guarded(42, GuardMetadata())
        schema = guarded_to_json(g)
        assert schema == {"type": "integer"}

    def test_to_json_guarded_dataclass_type(self):
        g = Guarded(Address, GuardMetadata())
        schema = guarded_to_json(g)
        assert schema["type"] == "object"
        assert schema["title"] == "Address"

    # -- Fallback --
    def test_to_json_guarded_unknown_type(self):
        """Un type inconnu tombe sur le fallback object."""
        g = Guarded(object(), GuardMetadata())
        schema = guarded_to_json(g)
        assert schema["type"] == "object"


# =================================================================== #
# 3. guarded_to_markdown tests                                        #
# =================================================================== #

class TestGuardedToMarkdown:
    """Génération de description textuelle optimisée pour LLM."""

    # -- Dataclass types --
    def test_to_markdown_dataclass_title(self):
        md = guarded_to_markdown(Address)
        assert "# Address" in md

    def test_to_markdown_dataclass_fields(self):
        md = guarded_to_markdown(Address)
        assert "**street**" in md
        assert "**city**" in md
        assert "**zip_code**" in md

    def test_to_markdown_dataclass_field_types(self):
        md = guarded_to_markdown(Address)
        assert "`str`" in md  # street and city
        assert "`int`" in md  # zip_code

    def test_to_markdown_dataclass_with_description(self):
        md = guarded_to_markdown(Address)
        assert "street" in md.lower() or "city" in md.lower()

    def test_to_markdown_nested_dataclass(self):
        md = guarded_to_markdown(Person)
        assert "# Person" in md
        assert "**name**" in md
        assert "**age**" in md
        assert "**address**" in md

    # -- Enum types --
    def test_to_markdown_enum_title(self):
        md = guarded_to_markdown(Color)
        assert "# Color" in md

    def test_to_markdown_enum_values(self):
        md = guarded_to_markdown(Color)
        assert "`red`" in md
        assert "`green`" in md
        assert "`blue`" in md

    def test_to_markdown_enum_member_names(self):
        md = guarded_to_markdown(Color)
        assert "RED" in md
        assert "GREEN" in md

    def test_to_markdown_int_enum(self):
        md = guarded_to_markdown(Priority)
        assert "# Priority" in md

    # -- Functions --
    def test_to_markdown_function_title(self):
        md = guarded_to_markdown(greet)
        assert "# greet" in md

    def test_to_markdown_function_signature(self):
        md = guarded_to_markdown(greet)
        assert "Signature" in md
        assert "name" in md

    def test_to_markdown_function_with_docstring(self):
        md = guarded_to_markdown(add)
        assert "Add" in md or "add" in md.lower()

    def test_to_markdown_function_parameters(self):
        md = guarded_to_markdown(add)
        assert "a" in md
        assert "b" in md

    # -- Guarded values --
    def test_to_markdown_guarded_dataclass_type(self):
        g = Guarded(Address, GuardMetadata())
        md = guarded_to_markdown(g)
        assert "# Address" in md

    def test_to_markdown_guarded_enum(self):
        g = Guarded(Color, GuardMetadata())
        md = guarded_to_markdown(g)
        assert "# Color" in md

    def test_to_markdown_guarded_primitive(self):
        g = Guarded(42, GuardMetadata())
        md = guarded_to_markdown(g)
        assert "42" in md
        assert "int" in md

    def test_to_markdown_guarded_function(self):
        g = Guarded(greet, GuardMetadata())
        md = guarded_to_markdown(g)
        assert "# greet" in md


# =================================================================== #
# 4. Cross-modal consistency                                            #
# =================================================================== #

class TestTriModalConsistency:
    """Les 3 modes doivent être cohérents pour un même type."""

    def test_all_modes_include_type_name(self):
        """Chaque mode inclut le nom du type."""
        py = guarded_to_python(Address)
        js = guarded_to_json(Address)
        md = guarded_to_markdown(Address)

        assert "Address" in py
        assert js["title"] == "Address"
        assert "# Address" in md

    def test_all_modes_include_field_info(self):
        """Chaque mode mentionne les champs du type."""
        py = guarded_to_python(Address)
        js = guarded_to_json(Address)
        md = guarded_to_markdown(Address)

        assert "street" in py
        assert "street" in js["properties"]
        assert "street" in md

    def test_enum_all_modes_consistent(self):
        """Les 3 modes produisent des résultats cohérents pour un Enum."""
        py = guarded_to_python(Color)
        js = guarded_to_json(Color)
        md = guarded_to_markdown(Color)

        assert "RED" in py
        assert "red" in js["enum"]
        assert "red" in md
