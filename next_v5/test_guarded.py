"""
Tests unitaires — OpenHosta.Guarded v5
=======================================

Couverture :
  1. GuardMetadata : création, addition, is_empty, repr
  2. GuardConfig    : valeurs par défaut et personnalisées
  3. Guarded[T]     : duck typing (getattr, ==, +, [], len, iter, bool, str, repr, hash, format, __call__)
  4. guard()        : primitives, nested list, nested dict, dataclass, nested mixed, no double-wrap
  5. unguard()      : extraction récursive list/dict/dataclass, identités
  6. guard_info()   : feuille, agrégation list, agrégation dict, dataclass, native → 0
  7. guarded_to_python / guarded_to_json / guarded_to_markdown
  8. REGISTRY       : register_layer, find_layer
"""

import dataclasses
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator

import pytest

# Importer depuis le module next_v5
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.dirname(__file__) or ".")

from openhosta import (
    GuardConfig,
    GuardMetadata,
    Guarded,
    guard,
    unguard,
    guard_info,
    guarded_to_python,
    guarded_to_json,
    guarded_to_markdown,
    REGISTRY,
)


# =================================================================== #
# Fixtures                                                             #
# =================================================================== #

@dataclass
class Address:
    street: str
    city: str
    zip_code: int


@dataclass
class Person:
    name: str
    age: int
    address: Address


class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


# =================================================================== #
# 1. GuardMetadata tests                                               #
# =================================================================== #

class TestGuardMetadata:
    def test_default_values(self):
        m = GuardMetadata()
        assert m.uncertainty == 0.0
        assert m.time_consumed == 0.0
        assert m.llm_logs == []
        assert m.heal_traces == []

    def test_custom_values(self):
        m = GuardMetadata(uncertainty=5.0, time_consumed=150.0)
        assert m.uncertainty == 5.0
        assert m.time_consumed == 150.0

    def test_addition(self):
        m1 = GuardMetadata(uncertainty=5.0, time_consumed=150.0, llm_logs=[{"a": 1}])
        m2 = GuardMetadata(uncertainty=10.0, time_consumed=300.0, heal_traces=["heal1"])
        m = m1 + m2
        assert m.uncertainty == 15.0
        assert m.time_consumed == 450.0
        assert len(m.llm_logs) == 1
        assert len(m.heal_traces) == 1
        assert m.heal_traces[0] == "heal1"

    def test_raddition(self):
        m1 = GuardMetadata(uncertainty=5.0)
        m2 = GuardMetadata(uncertainty=10.0)
        m = m2.__radd__(m1)
        assert m.uncertainty == 15.0

    def test_is_empty_true(self):
        m = GuardMetadata()
        assert m.is_empty() is True

    def test_is_empty_false(self):
        m = GuardMetadata(uncertainty=0.5)
        assert m.is_empty() is False

    def test_repr_contains_metrics(self):
        m = GuardMetadata(uncertainty=5.0, time_consumed=150.0)
        r = repr(m)
        assert "uncertainty=5.00" in r
        assert "time_consumed=150.0ms" in r


# =================================================================== #
# 2. GuardConfig tests                                                 #
# =================================================================== #

class TestGuardConfig:
    def test_defaults(self):
        c = GuardConfig()
        assert c.max_uncertainty == 1.0
        assert c.max_effort_ms == 120_000
        assert c.heal_retries_per_layer == 2

    def test_custom(self):
        c = GuardConfig(max_uncertainty=0.5, max_effort_ms=1000, heal_retries_per_layer=3)
        assert c.max_uncertainty == 0.5
        assert c.max_effort_ms == 1000
        assert c.heal_retries_per_layer == 3


# =================================================================== #
# 3. Guarded duck typing tests                                         #
# =================================================================== #

class TestGuardedDuckTyping:
    def test_str_uppercase(self):
        g = Guarded("hello world", GuardMetadata())
        assert g.upper() == "HELLO WORLD"

    def test_str_split(self):
        g = Guarded("a,b,c", GuardMetadata())
        assert g.split(",") == ["a", "b", "c"]

    def test_int_arithmetic(self):
        g = Guarded(42, GuardMetadata())
        assert int(g) == 42
        assert g + 1 == 43
        assert 1 + g == 43
        assert g * 2 == 84
        assert g - 2 == 40
        assert g / 2 == 21.0
        assert g // 2 == 21
        assert g % 5 == 2
        assert g ** 2 == 1764

    def test_float_format(self):
        g = Guarded(3.14159, GuardMetadata())
        assert f"{g:.2f}" == "3.14"

    def test_eq_with_native(self):
        g = Guarded("hello", GuardMetadata())
        assert g == "hello"
        assert not (g == "world")

    def test_eq_with_guarded(self):
        g1 = Guarded("hello", GuardMetadata(uncertainty=0.1))
        g2 = Guarded("hello", GuardMetadata(uncertainty=0.5))
        assert g1 == g2

    def test_comparison_operators(self):
        g = Guarded(5, GuardMetadata())
        assert g < 10
        assert g <= 5
        assert g > 2
        assert g >= 5

    def test_hash(self):
        g = Guarded("key", GuardMetadata())
        d = {"key": "val"}
        assert g in {g: 1}

    def test_bool_truthy(self):
        assert bool(Guarded("hello", GuardMetadata())) is True
        assert bool(Guarded(42, GuardMetadata())) is True

    def test_bool_falsy(self):
        assert bool(Guarded("", GuardMetadata())) is False
        assert bool(Guarded(0, GuardMetadata())) is False
        assert bool(Guarded(None, GuardMetadata())) is False

    def test_len(self):
        g = Guarded([1, 2, 3], GuardMetadata())
        assert len(g) == 3

    def test_contains(self):
        g = Guarded([1, 2, 3], GuardMetadata())
        assert 2 in g
        assert 5 not in g

    def test_getitem(self):
        g = Guarded([10, 20, 30], GuardMetadata())
        assert g[0] == 10
        assert g[1] == 20

    def test_iter(self):
        g = Guarded([1, 2, 3], GuardMetadata())
        assert list(g) == [1, 2, 3]

    def test_str_and_repr(self):
        g = Guarded(42, GuardMetadata())
        assert str(g) == "42"
        assert repr(g) == "42"

    def test_callable(self):
        def add(a, b): return a + b
        g = Guarded(add, GuardMetadata())
        assert g(3, 4) == 7

    def test_setattr_on_mutable(self):
        d = {"key": 1}
        g = Guarded(d, GuardMetadata())
        g["new_key"] = 2
        assert g["new_key"] == 2

    def test_neg_pos_abs(self):
        g = Guarded(-42, GuardMetadata())
        assert -g == 42
        assert +g == -42
        assert abs(g) == 42


# =================================================================== #
# 4. guard() tests                                                     #
# =================================================================== #

class TestGuard:
    def test_primitive_string(self):
        m = GuardMetadata(uncertainty=5.0, time_consumed=150.0)
        g = guard("hello", m)
        assert isinstance(g, Guarded)
        assert g._value == "hello"
        assert g._metadata.uncertainty == 5.0
        assert g._metadata.time_consumed == 150.0

    def test_primitive_int(self):
        g = guard(42, GuardMetadata())
        assert g._value == 42

    def test_no_metadata(self):
        g = guard("hello")
        assert g._value == "hello"
        assert g._metadata.is_empty()

    def test_already_guarded_returns_same(self):
        m = GuardMetadata(uncertainty=0.5)
        g1 = Guarded("hello", m)
        g2 = guard(g1)
        assert g1 is g2

    def test_list_aggregation(self):
        v1 = guard("Paris", GuardMetadata(uncertainty=5.0, time_consumed=150.0))
        v2 = guard("Lyon", GuardMetadata(uncertainty=10.0, time_consumed=300.0))
        v3 = "Marseille"  # native

        lst = guard([v1, v2, v3])
        info = guard_info(lst)
        assert info.uncertainty == 15.0  # 5 + 10 + 0
        assert info.time_consumed == 450.0  # 150 + 300 + 0

    def test_nested_list(self):
        v1 = guard("a", GuardMetadata(uncertainty=1.0))
        v2 = guard("b", GuardMetadata(uncertainty=2.0))
        nested = guard([[v1, v2]])
        info = guard_info(nested)
        assert info.uncertainty == 3.0

    def test_dict_aggregation(self):
        v1 = guard(10, GuardMetadata(uncertainty=3.0, time_consumed=100.0))
        d = guard({"x": v1, "y": 20})  # 20 is native → 0
        info = guard_info(d)
        assert info.uncertainty == 3.0
        assert info.time_consumed == 100.0

    def test_tuple(self):
        v1 = guard("a", GuardMetadata(uncertainty=1.0))
        t = guard((v1, "b"))
        assert isinstance(unguard(t), tuple)
        assert unguard(t) == ("a", "b")

    def test_dataclass(self):
        addr = Address(street="Rue de la Paix", city="Paris", zip_code=75001)
        addr_g = guard(addr, GuardMetadata(uncertainty=2.0))
        assert isinstance(addr_g, Guarded)
        # Duck typing : accéder aux champs
        assert addr_g.city == "Paris"
        assert addr_g.street == "Rue de la Paix"
        info = guard_info(addr_g)
        assert info.uncertainty == 2.0

    def test_nested_dataclass_with_guarded_fields(self):
        addr_inner = Address(
            street=guard("Rue", GuardMetadata(uncertainty=1.0)),
            city=guard("Paris", GuardMetadata(uncertainty=2.0)),
            zip_code=75001,  # native → 0
        )
        addr_g = guard(addr_inner)
        info = guard_info(addr_g)
        # street(1.0) + city(2.0) + zip_code(0) = 3.0
        assert info.uncertainty == 3.0

    def test_mixed_structure(self):
        v1 = guard("a", GuardMetadata(uncertainty=1.0, time_consumed=10.0))
        v2 = guard("b", GuardMetadata(uncertainty=2.0, time_consumed=20.0))
        mixed = guard({
            "tags": [v1, v2],
            "count": 3,  # native
        })
        info = guard_info(mixed)
        assert info.uncertainty == 3.0  # 1.0 + 2.0 + 0
        assert info.time_consumed == 30.0  # 10.0 + 20.0 + 0

    def test_spec_example_exactly(self):
        """Reproduction exacte de l'exemple 2 de guarded.md"""
        val1 = guard("Paris", GuardMetadata(uncertainty=5.0, time_consumed=150))
        val2 = guard("Lyon", GuardMetadata(uncertainty=10.0, time_consumed=300))
        native_val = "Marseille"

        city_list = guard([val1, val2, native_val])
        info = guard_info(city_list)
        assert info.time_consumed == 450.0
        assert info.uncertainty == 15.0

    def test_guard_with_metadata_on_list(self):
        """Le metadata passé au guard sur le parent s'ajoute à la somme des enfants."""
        v1 = guard("a", GuardMetadata(uncertainty=1.0))
        lst = guard([v1], GuardMetadata(uncertainty=5.0))
        info = guard_info(lst)
        assert info.uncertainty == 6.0  # parent 5.0 + child 1.0


# =================================================================== #
# 5. unguard() tests                                                   #
# =================================================================== #

class TestUnguard:
    def test_simple(self):
        g = Guarded("hello", GuardMetadata())
        assert unguard(g) == "hello"
        assert type(unguard(g)) is str

    def test_int(self):
        g = Guarded(42, GuardMetadata())
        assert unguard(g) == 42
        assert type(unguard(g)) is int

    def test_list(self):
        lst = [
            Guarded("a", GuardMetadata()),
            Guarded("b", GuardMetadata()),
            "c",  # native
        ]
        result = unguard(lst)
        assert result == ["a", "b", "c"]
        assert all(type(x) is str for x in result)

    def test_nested_list(self):
        nested = [
            [Guarded("x", GuardMetadata()), "y"],
            Guarded("z", GuardMetadata()),
        ]
        result = unguard(nested)
        assert result == [["x", "y"], "z"]

    def test_dict(self):
        d = {
            "name": Guarded("Alice", GuardMetadata()),
            "age": Guarded(30, GuardMetadata()),
            "active": True,
        }
        result = unguard(d)
        assert result == {"name": "Alice", "age": 30, "active": True}
        assert type(result["name"]) is str
        assert type(result["age"]) is int

    def test_dataclass(self):
        addr = Address(
            street=Guarded("Rue", GuardMetadata()),
            city=Guarded("Paris", GuardMetadata()),
            zip_code=75001,
        )
        result = unguard(addr)
        assert isinstance(result, Address)
        assert result.street == "Rue"
        assert result.city == "Paris"
        assert result.zip_code == 75001
        assert type(result.street) is str  # No longer Guarded

    def test_dataclass_nested(self):
        p = Person(
            name=Guarded("Alice", GuardMetadata()),
            age=Guarded(25, GuardMetadata()),
            address=Address(
                street=Guarded("Main", GuardMetadata()),
                city=Guarded("Paris", GuardMetadata()),
                zip_code=75001,
            ),
        )
        result = unguard(p)
        assert isinstance(result, Person)
        assert result.name == "Alice"
        assert result.address.city == "Paris"
        assert type(result.name) is str
        assert type(result.address.street) is str

    def test_identity_unguard_guard_unguard(self):
        """unguard(guard(unguard(g))) == unguard(g)"""
        original = Guarded("hello", GuardMetadata(uncertainty=0.5))
        cleaned = unguard(original)
        re_guarded = guard(cleaned)
        double_cleaned = unguard(re_guarded)
        assert double_cleaned == cleaned

    def test_unguard_native_returns_same(self):
        assert unguard(42) == 42
        assert unguard("hello") == "hello"
        assert unguard(None) is None

    def test_unguard_tuple(self):
        t = (Guarded(1, GuardMetadata()), Guarded(2, GuardMetadata()))
        result = unguard(t)
        assert isinstance(result, tuple)
        assert result == (1, 2)


# =================================================================== #
# 6. guard_info() tests                                                #
# =================================================================== #

class TestGuardInfo:
    def test_guarded_leaf(self):
        m = GuardMetadata(uncertainty=0.5, time_consumed=100.0)
        g = Guarded("hello", m)
        info = guard_info(g)
        assert info.uncertainty == 0.5
        assert info.time_consumed == 100.0

    def test_native_returns_zero(self):
        info = guard_info(42)
        assert info.is_empty()
        info2 = guard_info("hello")
        assert info2.is_empty()
        info3 = guard_info(None)
        assert info3.is_empty()

    def test_list_of_guarded(self):
        g1 = Guarded("a", GuardMetadata(uncertainty=1.0, time_consumed=10.0))
        g2 = Guarded("b", GuardMetadata(uncertainty=2.0, time_consumed=20.0))
        info = guard_info([g1, g2])
        assert info.uncertainty == 3.0
        assert info.time_consumed == 30.0

    def test_mixed_list(self):
        g = Guarded("a", GuardMetadata(uncertainty=5.0))
        info = guard_info([g, "b", 42])
        assert info.uncertainty == 5.0

    def test_dict_aggregation(self):
        g1 = Guarded("hello", GuardMetadata(uncertainty=3.0, time_consumed=60.0))
        info = guard_info({"name": g1, "age": 30})
        assert info.uncertainty == 3.0
        assert info.time_consumed == 60.0

    def test_dataclass_aggregation(self):
        addr = Address(
            street=Guarded("Rue", GuardMetadata(uncertainty=1.0, time_consumed=5.0)),
            city=Guarded("Paris", GuardMetadata(uncertainty=2.0, time_consumed=10.0)),
            zip_code=75001,
        )
        info = guard_info(addr)
        assert info.uncertainty == 3.0
        assert info.time_consumed == 15.0

    def test_deeply_nested(self):
        g1 = Guarded("a", GuardMetadata(uncertainty=1.0))
        g2 = Guarded("b", GuardMetadata(uncertainty=2.0))
        g3 = Guarded("c", GuardMetadata(uncertainty=3.0))
        nested = [[g1, g2], { "x": g3 }]
        info = guard_info(nested)
        assert info.uncertainty == 6.0  # 1+2+3


# =================================================================== #
# 7. Tri-modal tests                                                    #
# =================================================================== #

class TestTriModal:
    def test_to_python_function(self):
        def add(a: int, b: int) -> int:
            return a + b
        code = guarded_to_python(add)
        assert "def add" in code
        assert "a: int" in code
        assert "b: int" in code

    def test_to_python_dataclass_type(self):
        code = guarded_to_python(Address)
        assert "@dataclasses.dataclass" in code
        assert "class Address:" in code
        assert "street:" in code
        assert "city:" in code

    def test_to_python_enum_type(self):
        code = guarded_to_python(Color)
        assert "class Color(Enum):" in code
        assert "RED" in code
        assert "RED = 'red'" in code or 'RED = "red"' in code

    def test_to_python_value(self):
        code = guarded_to_python(42)
        assert "type: int" in code
        assert "42" in code

    def test_to_python_guarded_value(self):
        g = Guarded(42, GuardMetadata())
        code = guarded_to_python(g)
        assert "type: int" in code

    def test_to_json_string(self):
        assert guarded_to_json("hello") == {"type": "string"}

    def test_to_json_int(self):
        assert guarded_to_json(42) == {"type": "integer"}

    def test_to_json_float(self):
        assert guarded_to_json(3.14) == {"type": "number"}

    def test_to_json_bool(self):
        assert guarded_to_json(True) == {"type": "boolean"}

    def test_to_json_null(self):
        assert guarded_to_json(None) == {"type": "null"}

    def test_to_json_enum(self):
        schema = guarded_to_json(Color)
        assert schema["type"] == "string"
        assert schema["enum"] == ["red", "green", "blue"]

    def test_to_json_dataclass(self):
        schema = guarded_to_json(Address)
        assert schema["type"] == "object"
        assert "street" in schema["properties"]
        assert "city" in schema["properties"]
        assert "street" in schema["required"]

    def test_to_markdown_dataclass(self):
        md = guarded_to_markdown(Address)
        assert "# Address" in md
        assert "**street**" in md
        assert "**city**" in md

    def test_to_markdown_enum(self):
        md = guarded_to_markdown(Color)
        assert "# Color" in md
        assert "`red`" in md

    def test_to_markdown_function(self):
        def greet(name: str) -> str:
            """Say hello."""
            return f"Hello, {name}"
        md = guarded_to_markdown(greet)
        assert "# greet" in md
        assert "Signature:" in md


# =================================================================== #
# 8. REGISTRY tests                                                     #
# =================================================================== #

class TestRegistry:
    def test_default_layers_exist(self):
        layers = REGISTRY.get_layers()
        names = [l.name for l in layers]
        assert "primitive" in names
        assert "enum" in names

    def test_find_primitive(self):
        layer = REGISTRY.find_layer("hello")
        assert layer is not None
        assert layer.name == "primitive"

    def test_find_enum(self):
        layer = REGISTRY.find_layer(Color.RED)
        assert layer is not None
        assert layer.name == "enum"

    def test_find_unknown_returns_none(self):
        layer = REGISTRY.find_layer({"custom": True})
        assert layer is None

    def test_register_and_find_custom(self):
        def is_custom(obj):
            return isinstance(obj, dict) and obj.get("custom")

        def custom_logic(obj):
            return Guarded(obj, GuardMetadata())

        REGISTRY.register_layer("custom", is_custom, custom_logic)
        layer = REGISTRY.find_layer({"custom": True})
        assert layer is not None
        assert layer.name == "custom"


# =================================================================== #
# 9. Integration: Spec alignment                                        #
# =================================================================== #

class TestSpecAlignment:
    """Tests qui vérifient l'alignement avec guarded.md Spec Section 5."""

    def test_spec_example_2_aggregation(self):
        """Exemple 2 : Agrégation Récursive des Coûts"""
        val1 = guard("Paris", GuardMetadata(uncertainty=5.0, time_consumed=150))
        val2 = guard("Lyon", GuardMetadata(uncertainty=10.0, time_consumed=300))
        native_val = "Marseille"  # incertitude 0, cout 0

        city_list = guard([val1, val2, native_val])
        info = guard_info(city_list)

        assert info.time_consumed == 450.0, "Expected 450ms total (150+300+0)"
        assert info.uncertainty == 15.0, "Expected 15.0% total (5+10+0)"

    def test_duck_typing_comparison(self):
        """Exemple 1 : DX Parfaite — comparison directe"""
        enum_g = Guarded(Color.RED, GuardMetadata())
        assert enum_g == Color.RED  # Le linter et le runtime acceptent

    def test_unguard_export_clean(self):
        """Exemple 4 : Exportation propre"""
        g = Guarded("Hello", GuardMetadata(uncertainty=0.1))
        clean = unguard(g)
        assert type(clean) is str
        assert clean == "Hello"
        # Plus de GuardMetadata dans le résultat
