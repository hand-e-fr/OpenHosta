"""
Tests unitaires — Guarded[T] V5 : Construction, Duck Typing, Opérateurs
=========================================================================

Couverture :
  - Construction Guarded(value, metadata) avec/sans metadata
  - Accès _value et _metadata
  - Duck typing : getattr délègue à la valeur sous-jacente
  - Opérateurs de comparaison : ==, !=, <, <=, >, >=
  - Opérateurs arithmétiques : +, -, *, /, //, %, **, neg, pos, abs
  - Protocoles container : len, iter, contains, getitem, setitem, delitem
  - Protocoles identité/hash/repr : bool, hash, repr, str, __format__
  - Protocole callable
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

from openhosta import Guarded, GuardMetadata


# --------------------------------------------------------------------------- #
# Fixtures                                                                      #
# --------------------------------------------------------------------------- #

@dataclass
class Address:
    street: str
    city: str
    zip_code: int


class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


@pytest.fixture
def meta():
    return GuardMetadata(uncertainty=0.5, time_consumed=100.0)


@pytest.fixture
def empty_meta():
    return GuardMetadata()


# =================================================================== #
# 1. Construction                                                       #
# =================================================================== #

class TestGuardedConstruction:
    """Guarded(value, metadata) — construction et accès aux champs internes."""

    def test_construction_string(self, meta):
        g = Guarded("hello", meta)
        assert g._value == "hello"
        assert g._metadata is meta

    def test_construction_int(self, meta):
        g = Guarded(42, meta)
        assert g._value == 42
        assert g._metadata.uncertainty == 0.5

    def test_construction_without_metadata(self):
        g = Guarded("hello")
        assert g._value == "hello"
        assert g._metadata.is_empty()

    def test_construction_none(self, meta):
        g = Guarded(None, meta)
        assert g._value is None
        assert g._metadata is meta

    def test_construction_list(self, meta):
        g = Guarded([1, 2, 3], meta)
        assert g._value == [1, 2, 3]

    def test_construction_dict(self, meta):
        g = Guarded({"a": 1}, meta)
        assert g._value == {"a": 1}

    def test_construction_dataclass(self, meta):
        addr = Address("Rue", "Paris", 75001)
        g = Guarded(addr, meta)
        assert g._value is addr

    def test_construction_enum(self, meta):
        g = Guarded(Color.RED, meta)
        assert g._value is Color.RED

    def test_construction_float(self, meta):
        g = Guarded(3.14, meta)
        assert g._value == 3.14

    def test_construction_bool_true(self, meta):
        g = Guarded(True, meta)
        assert g._value is True

    def test_construction_bool_false(self, meta):
        g = Guarded(False, meta)
        assert g._value is False

    def test_construction_tuple(self, meta):
        g = Guarded((1, 2), meta)
        assert g._value == (1, 2)

    def test_construction_guarded_nested(self, meta):
        """Un Guarded peut contenir un autre Guarded."""
        inner = Guarded("inner", GuardMetadata(uncertainty=0.1))
        outer = Guarded(inner, meta)
        assert outer._value is inner
        assert isinstance(outer._value, Guarded)


# =================================================================== #
# 2. Duck Typing — getattr delegation                                     #
# =================================================================== #

class TestGuardedDuckTyping:
    """Guarded délègue tous les attributs/méthodes à la valeur sous-jacente."""

    def test_str_uppercase(self):
        g = Guarded("hello world", GuardMetadata())
        assert g.upper() == "HELLO WORLD"

    def test_str_split(self):
        g = Guarded("a,b,c", GuardMetadata())
        assert g.split(",") == ["a", "b", "c"]

    def test_str_strip(self):
        g = Guarded("  hello  ", GuardMetadata())
        assert g.strip() == "hello"

    def test_str_startswith(self):
        g = Guarded("hello", GuardMetadata())
        assert g.startswith("hel") is True
        assert g.startswith("bye") is False

    def test_list_append_mutable(self):
        lst = [1, 2]
        g = Guarded(lst, GuardMetadata())
        g.append(3)
        assert g._value == [1, 2, 3]

    def test_dict_keys(self):
        g = Guarded({"a": 1, "b": 2}, GuardMetadata())
        assert set(g.keys()) == {"a", "b"}

    def test_dict_values(self):
        g = Guarded({"x": 10}, GuardMetadata())
        assert list(g.values()) == [10]

    def test_dataclass_field_access(self):
        addr = Address("Rue", "Paris", 75001)
        g = Guarded(addr, GuardMetadata())
        assert g.city == "Paris"
        assert g.street == "Rue"

    def test_enum_value_access(self):
        g = Guarded(Color.RED, GuardMetadata())
        assert g.value == "red"
        assert g.name == "RED"

    def test_list_len_via_method(self):
        g = Guarded([1, 2, 3], GuardMetadata())
        assert len(g) == 3  # via __len__


# =================================================================== #
# 3. Opérateurs de comparaison                                          #
# =================================================================== #

class TestComparisonOperators:
    """== , !=, < , <= , > , >=  avec valeurs natives et Guarded."""

    def test_eq_with_native(self):
        g = Guarded("hello", GuardMetadata(uncertainty=0.1))
        assert g == "hello"

    def test_eq_with_different_native(self):
        g = Guarded("hello", GuardMetadata())
        assert g != "world"

    def test_eq_with_guarded_same_value(self):
        g1 = Guarded("hello", GuardMetadata(uncertainty=0.1))
        g2 = Guarded("hello", GuardMetadata(uncertainty=0.5))
        assert g1 == g2

    def test_eq_with_guarded_different_value(self):
        g1 = Guarded("hello", GuardMetadata())
        g2 = Guarded("world", GuardMetadata())
        assert not (g1 == g2)

    def test_ne_with_native(self):
        g = Guarded(42, GuardMetadata())
        assert g != 43
        assert not (g != 42)

    def test_lt(self):
        g = Guarded(5, GuardMetadata())
        assert g < 10
        assert not (g < 3)
        assert not (g < 5)

    def test_le(self):
        g = Guarded(5, GuardMetadata())
        assert g <= 5
        assert g <= 10
        assert not (g <= 4)

    def test_gt(self):
        g = Guarded(5, GuardMetadata())
        assert g > 2
        assert not (g > 5)
        assert not (g > 10)

    def test_ge(self):
        g = Guarded(5, GuardMetadata())
        assert g >= 5
        assert g >= 3
        assert not (g >= 6)

    def test_eq_with_guarded_unguarded(self):
        """Comparaison avec un autre Guarded qui contient un Guarded."""
        inner = Guarded(5, GuardMetadata())
        outer = Guarded(inner, GuardMetadata())
        assert outer == 5  # outer._value is inner (Guarded), but __eq__ delegates

    def test_eq_int_vs_float(self):
        g = Guarded(5, GuardMetadata())
        assert g == 5.0

    def test_eq_string_unicode(self):
        g = Guarded("café", GuardMetadata())
        assert g == "café"


# =================================================================== #
# 4. Opérateurs arithmétiques                                           #
# =================================================================== #

class TestArithmeticOperators:
    """+, -, *, /, //, %, **, -g, +g, abs(g) avec valeurs natives et Guarded."""

    def test_add_with_native(self):
        g = Guarded(42, GuardMetadata())
        assert g + 1 == 43

    def test_radd(self):
        g = Guarded(42, GuardMetadata())
        assert 1 + g == 43

    def test_sub(self):
        g = Guarded(42, GuardMetadata())
        assert g - 2 == 40

    def test_rsub(self):
        g = Guarded(42, GuardMetadata())
        assert 100 - g == 58

    def test_mul(self):
        g = Guarded(6, GuardMetadata())
        assert g * 7 == 42

    def test_rmul(self):
        g = Guarded(6, GuardMetadata())
        assert 7 * g == 42

    def test_truediv(self):
        g = Guarded(10, GuardMetadata())
        assert g / 2 == 5.0

    def test_rtruediv(self):
        g = Guarded(2, GuardMetadata())
        assert 10 / g == 5.0

    def test_floordiv(self):
        g = Guarded(10, GuardMetadata())
        assert g // 3 == 3

    def test_mod(self):
        g = Guarded(10, GuardMetadata())
        assert g % 3 == 1

    def test_pow(self):
        g = Guarded(3, GuardMetadata())
        assert g ** 2 == 9

    def test_neg(self):
        g = Guarded(-42, GuardMetadata())
        assert -g == 42

    def test_pos(self):
        g = Guarded(-42, GuardMetadata())
        assert +g == -42

    def test_abs(self):
        g = Guarded(-42, GuardMetadata())
        assert abs(g) == 42

    def test_add_string_concatenation(self):
        g = Guarded("hello ", GuardMetadata())
        assert g + "world" == "hello world"

    def test_radd_string_concatenation(self):
        g = Guarded("world", GuardMetadata())
        assert "hello " + g == "hello world"

    def test_mul_string_repeat(self):
        g = Guarded("ab", GuardMetadata())
        assert g * 3 == "ababab"

    def test_arithmetic_with_guarded_other(self):
        """Arithmétique entre deux Guarded."""
        g1 = Guarded(10, GuardMetadata(uncertainty=0.1))
        g2 = Guarded(3, GuardMetadata(uncertainty=0.2))
        assert g1 + g2 == 13
        assert g1 - g2 == 7
        assert g1 * g2 == 30


# =================================================================== #
# 5. Protocoles container                                               #
# =================================================================== #

class TestContainerProtocols:
    """len, iter, contains, getitem, setitem, delitem."""

    def test_len_string(self):
        g = Guarded("hello", GuardMetadata())
        assert len(g) == 5

    def test_len_list(self):
        g = Guarded([1, 2, 3], GuardMetadata())
        assert len(g) == 3

    def test_len_dict(self):
        g = Guarded({"a": 1, "b": 2}, GuardMetadata())
        assert len(g) == 2

    def test_iter_list(self):
        g = Guarded([1, 2, 3], GuardMetadata())
        assert list(g) == [1, 2, 3]

    def test_iter_string(self):
        g = Guarded("abc", GuardMetadata())
        assert list(g) == ["a", "b", "c"]

    def test_contains_list(self):
        g = Guarded([1, 2, 3], GuardMetadata())
        assert 2 in g
        assert 5 not in g

    def test_contains_string(self):
        g = Guarded("hello", GuardMetadata())
        assert "ell" in g
        assert "xyz" not in g

    def test_getitem_list(self):
        g = Guarded([10, 20, 30], GuardMetadata())
        assert g[0] == 10
        assert g[1] == 20
        assert g[-1] == 30

    def test_getitem_string(self):
        g = Guarded("hello", GuardMetadata())
        assert g[0] == "h"
        assert g[1:3] == "el"

    def test_getitem_dict(self):
        g = Guarded({"a": 1, "b": 2}, GuardMetadata())
        assert g["a"] == 1
        assert g["b"] == 2

    def test_setitem_list(self):
        lst = [1, 2, 3]
        g = Guarded(lst, GuardMetadata())
        g[0] = 99
        assert lst[0] == 99

    def test_setitem_dict(self):
        d = {"a": 1}
        g = Guarded(d, GuardMetadata())
        g["b"] = 2
        assert d["b"] == 2

    def test_delitem_list(self):
        lst = [1, 2, 3]
        g = Guarded(lst, GuardMetadata())
        del g[0]
        assert lst == [2, 3]

    def test_delitem_dict(self):
        d = {"a": 1, "b": 2}
        g = Guarded(d, GuardMetadata())
        del g["a"]
        assert d == {"b": 2}


# =================================================================== #
# 6. Protocoles identité / hash / repr                                  #
# =================================================================== #

class TestIdentityProtocols:
    """bool, hash, repr, str, __format__, __index__."""

    def test_bool_truthy_string(self):
        assert bool(Guarded("hello", GuardMetadata())) is True

    def test_bool_truthy_int(self):
        assert bool(Guarded(42, GuardMetadata())) is True

    def test_bool_truthy_list(self):
        assert bool(Guarded([1], GuardMetadata())) is True

    def test_bool_falsy_empty_string(self):
        assert bool(Guarded("", GuardMetadata())) is False

    def test_bool_falsy_zero(self):
        assert bool(Guarded(0, GuardMetadata())) is False

    def test_bool_falsy_none(self):
        assert bool(Guarded(None, GuardMetadata())) is False

    def test_bool_falsy_empty_list(self):
        assert bool(Guarded([], GuardMetadata())) is False

    def test_bool_falsy_false(self):
        assert bool(Guarded(False, GuardMetadata())) is False

    def test_hash_in_dict_key(self):
        g = Guarded("key", GuardMetadata())
        d = {g: 1}
        assert d[g] == 1
        assert d["key"] == 1  # Same hash as native "key"

    def test_hash_int(self):
        g = Guarded(42, GuardMetadata())
        assert hash(g) == hash(42)

    def test_hash_in_set(self):
        g = Guarded("a", GuardMetadata())
        s = {g, "b"}
        assert "a" in s
        assert len(s) == 2

    def test_repr_int(self):
        g = Guarded(42, GuardMetadata())
        assert repr(g) == "42"

    def test_repr_string(self):
        g = Guarded("hello", GuardMetadata())
        assert repr(g) == "'hello'"

    def test_repr_float(self):
        g = Guarded(3.14, GuardMetadata())
        assert repr(g) == "3.14"

    def test_repr_enum(self):
        g = Guarded(Color.RED, GuardMetadata())
        assert repr(g) == repr(Color.RED)

    def test_str_int(self):
        g = Guarded(42, GuardMetadata())
        assert str(g) == "42"

    def test_str_string(self):
        g = Guarded("hello", GuardMetadata())
        assert str(g) == "hello"

    def test_format_float_precision(self):
        g = Guarded(3.14159, GuardMetadata())
        assert f"{g:.2f}" == "3.14"

    def test_format_string(self):
        g = Guarded("world", GuardMetadata())
        assert f"Hello, {g}!" == "Hello, world!"

    def test_index_as_list_index(self):
        g = Guarded(2, GuardMetadata())
        lst = ["a", "b", "c"]
        assert lst[g] == "c"


# =================================================================== #
# 7. Protocole callable                                                 #
# =================================================================== #

class TestCallableProtocol:
    """__call__ délègue à la valeur sous-jacente si elle est callable."""

    def test_call_function(self):
        def add(a, b):
            return a + b
        g = Guarded(add, GuardMetadata())
        assert g(3, 4) == 7

    def test_call_lambda(self):
        g = Guarded(lambda x: x * 2, GuardMetadata())
        assert g(5) == 10

    def test_call_method_bound(self):
        s = "hello"
        g = Guarded(s.upper, GuardMetadata())
        assert g() == "HELLO"

    def test_call_class_constructor(self):
        g = Guarded(int, GuardMetadata())
        assert g("42") == 42
