"""
Tests unitaires — Guarded[T] V5 : Fonctions core API (guard, unguard, guard_info)
==================================================================================

Couverture :
  - guard() : primitives, pas de double-wrap, listes, dicts, tuples, dataclasses, agrégation métadonnées
  - unguard() : extraction feuille, listes, dicts, tuples, dataclasses, nested, objets natifs inchangés
  - guard_info() : feuille, agrégation liste/dict/dataclass, objet natif → GuardMetadata vide
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
    guard,
    unguard,
    guard_info,
)


# --------------------------------------------------------------------------- #
# Fixtures                                                                      #
# --------------------------------------------------------------------------- #

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


class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


# =================================================================== #
# 1. guard() tests                                                          #
# =================================================================== #

class TestGuard:
    """Encapsulation récursive avec agrégation des métadonnées."""

    # -- Primitives --
    def test_guard_primitive_string(self):
        m = GuardMetadata(uncertainty=5.0, time_consumed=150.0)
        g = guard("hello", m)
        assert isinstance(g, Guarded)
        assert g._value == "hello"
        assert g._metadata.uncertainty == 5.0
        assert g._metadata.time_consumed == 150.0

    def test_guard_primitive_int(self):
        g = guard(42, GuardMetadata())
        assert isinstance(g, Guarded)
        assert g._value == 42

    def test_guard_primitive_float(self):
        g = guard(3.14, GuardMetadata())
        assert g._value == 3.14

    def test_guard_primitive_bool(self):
        g = guard(True, GuardMetadata())
        assert g._value is True

    def test_guard_primitive_none(self):
        g = guard(None, GuardMetadata())
        assert g._value is None

    def test_guard_no_metadata(self):
        g = guard("hello")
        assert g._value == "hello"
        assert g._metadata.is_empty()

    # -- No double-wrap --
    def test_guard_already_guarded_returns_same(self):
        m = GuardMetadata(uncertainty=0.5)
        g1 = Guarded("hello", m)
        g2 = guard(g1)
        assert g1 is g2  # Identity — pas de double enveloppe

    def test_nested_guard_no_triple_wrap(self):
        m = GuardMetadata(uncertainty=0.3)
        g1 = guard("hello", m)
        g2 = guard(g1)
        g3 = guard(g2)
        assert g1 is g2 is g3

    # -- Lists --
    def test_guard_list_primitive(self):
        g = guard([1, 2, 3], GuardMetadata(uncertainty=1.0, time_consumed=10.0))
        value = g._value
        assert isinstance(value, list)
        assert len(value) == 3
        assert all(isinstance(item, Guarded) for item in value)
        # Parent metadata includes explicit 1.0 + children 0
        info = guard_info(g)
        assert info.uncertainty == 1.0
        assert info.time_consumed == 10.0

    def test_guard_list_with_guarded_items_aggregation(self):
        v1 = guard("Paris", GuardMetadata(uncertainty=5.0, time_consumed=150.0))
        v2 = guard("Lyon", GuardMetadata(uncertainty=10.0, time_consumed=300.0))
        v3 = "Marseille"  # native → uncertainty 0

        lst = guard([v1, v2, v3])
        info = guard_info(lst)
        assert info.uncertainty == 15.0  # 5 + 10 + 0
        assert info.time_consumed == 450.0  # 150 + 300 + 0

    def test_guard_list_with_parent_metadata(self):
        """Le metadata du parent s'ajoute à la somme des enfants."""
        v1 = guard("a", GuardMetadata(uncertainty=1.0))
        lst = guard([v1], GuardMetadata(uncertainty=5.0))
        info = guard_info(lst)
        assert info.uncertainty == 6.0  # parent 5.0 + child 1.0

    def test_guard_nested_list(self):
        v1 = guard("x", GuardMetadata(uncertainty=1.0))
        v2 = guard("y", GuardMetadata(uncertainty=2.0))
        nested = guard([[v1, v2]])
        info = guard_info(nested)
        assert info.uncertainty == 3.0  # 1 + 2

    def test_guard_empty_list(self):
        g = guard([], GuardMetadata(uncertainty=2.0))
        info = guard_info(g)
        assert info.uncertainty == 2.0  # Only parent metadata

    # -- Dicts --
    def test_guard_dict_aggregation(self):
        v1 = guard(10, GuardMetadata(uncertainty=3.0, time_consumed=100.0))
        d = guard({"x": v1, "y": 20})  # 20 is native → 0
        info = guard_info(d)
        assert info.uncertainty == 3.0
        assert info.time_consumed == 100.0

    def test_guard_dict_all_guarded(self):
        v1 = guard("a", GuardMetadata(uncertainty=1.0, time_consumed=10.0))
        v2 = guard("b", GuardMetadata(uncertainty=2.0, time_consumed=20.0))
        d = guard({"k1": v1, "k2": v2})
        info = guard_info(d)
        assert info.uncertainty == 3.0
        assert info.time_consumed == 30.0

    def test_guard_empty_dict(self):
        g = guard({}, GuardMetadata(uncertainty=1.0))
        info = guard_info(g)
        assert info.uncertainty == 1.0

    # -- Tuples --
    def test_guard_tuple_preserves_type(self):
        v1 = guard("a", GuardMetadata(uncertainty=1.0))
        t = guard((v1, "b"))
        assert isinstance(unguard(t), tuple)
        assert unguard(t) == ("a", "b")

    def test_guard_tuple_aggregation(self):
        v1 = guard("a", GuardMetadata(uncertainty=1.0, time_consumed=10.0))
        v2 = guard("b", GuardMetadata(uncertainty=2.0, time_consumed=20.0))
        t = guard((v1, v2))
        info = guard_info(t)
        assert info.uncertainty == 3.0
        assert info.time_consumed == 30.0

    # -- Dataclasses --
    def test_guard_dataclass(self):
        addr = Address(street="Rue de la Paix", city="Paris", zip_code=75001)
        addr_g = guard(addr, GuardMetadata(uncertainty=2.0))
        assert isinstance(addr_g, Guarded)
        # Duck typing : accéder aux champs
        assert addr_g.city == "Paris"
        assert addr_g.street == "Rue de la Paix"
        info = guard_info(addr_g)
        assert info.uncertainty == 2.0

    def test_guard_dataclass_with_guarded_fields(self):
        addr_inner = Address(
            street=guard("Rue", GuardMetadata(uncertainty=1.0)),
            city=guard("Paris", GuardMetadata(uncertainty=2.0)),
            zip_code=75001,  # native → 0
        )
        addr_g = guard(addr_inner)
        info = guard_info(addr_g)
        # street(1.0) + city(2.0) + zip_code(0) = 3.0
        assert info.uncertainty == 3.0

    def test_guard_nested_dataclass(self):
        """Dataclass imbriqué (Person → Address) avec champs mixtes."""
        person = Person(
            name=guard("Alice", GuardMetadata(uncertainty=0.5, time_consumed=50.0)),
            age=30,  # native → 0
            address=Address(
                street=guard("Main St", GuardMetadata(uncertainty=1.0)),
                city="Paris",
                zip_code=75001,
            ),
        )
        p_g = guard(person)
        info = guard_info(p_g)
        # name(0.5) + age(0) + addr.street(1.0) + addr.city(0) + addr.zip(0) = 1.5
        assert info.uncertainty == 1.5
        assert info.time_consumed == 50.0  # Only name has time_consumed=50

    # -- Mixed structures --
    def test_guard_mixed_structure(self):
        v1 = guard("a", GuardMetadata(uncertainty=1.0, time_consumed=10.0))
        v2 = guard("b", GuardMetadata(uncertainty=2.0, time_consumed=20.0))
        mixed = guard({
            "tags": [v1, v2],
            "count": 3,  # native → 0
        })
        info = guard_info(mixed)
        assert info.uncertainty == 3.0  # 1.0 + 2.0 + 0
        assert info.time_consumed == 30.0  # 10.0 + 20.0 + 0

    # -- Enum --
    def test_guard_enum_primitive(self):
        g = guard(Status.ACTIVE, GuardMetadata(uncertainty=0.5))
        assert g._value is Status.ACTIVE

    def test_guard_enum_via_registry(self):
        g = guard(Status.ACTIVE)
        info = guard_info(g)
        # Enum goes through registry layer, metadata should be empty
        assert info.is_empty()


# =================================================================== #
# 2. unguard() tests                                                      #
# =================================================================== #

class TestUnguard:
    """Extraction récursive de la valeur native."""

    def test_unguard_simple_string(self):
        g = Guarded("hello", GuardMetadata())
        assert unguard(g) == "hello"
        assert type(unguard(g)) is str

    def test_unguard_int(self):
        g = Guarded(42, GuardMetadata())
        assert unguard(g) == 42
        assert type(unguard(g)) is int

    def test_unguard_float(self):
        g = Guarded(3.14, GuardMetadata())
        assert unguard(g) == 3.14
        assert type(unguard(g)) is float

    def test_unguard_none(self):
        g = Guarded(None, GuardMetadata())
        assert unguard(g) is None

    def test_unguard_bool_true(self):
        g = Guarded(True, GuardMetadata())
        assert unguard(g) is True

    def test_unguard_bool_false(self):
        g = Guarded(False, GuardMetadata())
        assert unguard(g) is False

    def test_unguard_list(self):
        lst = [
            Guarded("a", GuardMetadata()),
            Guarded("b", GuardMetadata()),
            "c",  # native
        ]
        result = unguard(lst)
        assert result == ["a", "b", "c"]
        assert all(type(x) is str for x in result)

    def test_unguard_nested_list(self):
        nested = [
            [Guarded("x", GuardMetadata()), "y"],
            Guarded("z", GuardMetadata()),
        ]
        result = unguard(nested)
        assert result == [["x", "y"], "z"]
        # Check no Guarded remains
        for sublist in result:
            for item in sublist:
                assert not isinstance(item, Guarded)

    def test_unguard_tuple(self):
        t = (Guarded(1, GuardMetadata()), Guarded(2, GuardMetadata()))
        result = unguard(t)
        assert isinstance(result, tuple)
        assert result == (1, 2)

    def test_unguard_dict(self):
        d = {
            "name": Guarded("Alice", GuardMetadata()),
            "age": Guarded(30, GuardMetadata()),
            "active": True,
        }
        result = unguard(d)
        assert result == {"name": "Alice", "age": 30, "active": True}
        assert type(result["name"]) is str
        assert type(result["age"]) is int

    def test_unguard_dataclass(self):
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

    def test_unguard_nested_dataclass(self):
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

    def test_unguard_mixed_dict_list(self):
        data = {
            "items": [
                Guarded("a", GuardMetadata()),
                Guarded("b", GuardMetadata()),
            ],
            "meta": {
                "version": Guarded(1, GuardMetadata()),
                "label": "v1",
            }
        }
        result = unguard(data)
        assert result == {
            "items": ["a", "b"],
            "meta": {"version": 1, "label": "v1"},
        }

    def test_unguard_native_int_returns_same(self):
        assert unguard(42) == 42
        assert type(unguard(42)) is int

    def test_unguard_native_string_returns_same(self):
        assert unguard("hello") == "hello"
        assert type(unguard("hello")) is str

    def test_unguard_native_none_returns_same(self):
        assert unguard(None) is None

    def test_unguard_native_list_no_guarded(self):
        assert unguard([1, 2, 3]) == [1, 2, 3]

    def test_unguard_native_dict_no_guarded(self):
        assert unguard({"a": 1, "b": 2}) == {"a": 1, "b": 2}

    # -- Identity roundtrip --
    def test_identity_unguard_guard_unguard(self):
        """unguard(guard(unguard(g))) == unguard(g)"""
        original = Guarded("hello", GuardMetadata(uncertainty=0.5))
        cleaned = unguard(original)
        re_guarded = guard(cleaned)
        double_cleaned = unguard(re_guarded)
        assert double_cleaned == cleaned

    def test_unguard_guard_dataclass_identity(self):
        addr = Address("Rue", "Paris", 75001)
        g = guard(addr)
        clean = unguard(g)
        assert clean == addr
        assert isinstance(clean, Address)

    def test_unguard_guard_list_identity(self):
        original = [1, 2, 3]
        g = guard(original, GuardMetadata())
        clean = unguard(g)
        assert clean == [1, 2, 3]
        assert all(type(x) is int for x in clean)


# =================================================================== #
# 3. guard_info() tests                                                   #
# =================================================================== #

class TestGuardInfo:
    """Observabilité : expose les métadonnées agrégées."""

    def test_guard_info_leaf(self):
        m = GuardMetadata(uncertainty=0.5, time_consumed=100.0)
        g = Guarded("hello", m)
        info = guard_info(g)
        assert info.uncertainty == 0.5
        assert info.time_consumed == 100.0

    def test_guard_info_with_logs(self):
        m = GuardMetadata(
            uncertainty=0.3,
            time_consumed=50.0,
            llm_logs=[{"call": 1}],
            heal_traces=["step1"],
        )
        g = Guarded("result", m)
        info = guard_info(g)
        assert info.uncertainty == 0.3
        assert info.time_consumed == 50.0
        assert len(info.llm_logs) == 1
        assert len(info.heal_traces) == 1

    def test_guard_info_native_int_returns_zero(self):
        info = guard_info(42)
        assert info.is_empty()

    def test_guard_info_native_string_returns_zero(self):
        info = guard_info("hello")
        assert info.is_empty()

    def test_guard_info_native_none_returns_zero(self):
        info = guard_info(None)
        assert info.is_empty()

    def test_guard_info_native_list_returns_zero(self):
        info = guard_info([1, 2, 3])
        assert info.is_empty()

    def test_guard_info_native_dict_returns_zero(self):
        info = guard_info({"a": 1, "b": 2})
        assert info.is_empty()

    def test_guard_info_list_of_guarded(self):
        g1 = Guarded("a", GuardMetadata(uncertainty=1.0, time_consumed=10.0))
        g2 = Guarded("b", GuardMetadata(uncertainty=2.0, time_consumed=20.0))
        info = guard_info([g1, g2])
        assert info.uncertainty == 3.0
        assert info.time_consumed == 30.0

    def test_guard_info_mixed_list(self):
        g = Guarded("a", GuardMetadata(uncertainty=5.0))
        info = guard_info([g, "b", 42])
        assert info.uncertainty == 5.0  # Only g contributes
        assert info.time_consumed == 0.0  # g has no time_consumed

    def test_guard_info_dict_aggregation(self):
        g1 = Guarded("hello", GuardMetadata(uncertainty=3.0, time_consumed=60.0))
        info = guard_info({"name": g1, "age": 30})
        assert info.uncertainty == 3.0
        assert info.time_consumed == 60.0

    def test_guard_info_dataclass_aggregation(self):
        addr = Address(
            street=Guarded("Rue", GuardMetadata(uncertainty=1.0, time_consumed=5.0)),
            city=Guarded("Paris", GuardMetadata(uncertainty=2.0, time_consumed=10.0)),
            zip_code=75001,
        )
        info = guard_info(addr)
        assert info.uncertainty == 3.0
        assert info.time_consumed == 15.0

    def test_guard_info_deeply_nested(self):
        g1 = Guarded("a", GuardMetadata(uncertainty=1.0))
        g2 = Guarded("b", GuardMetadata(uncertainty=2.0))
        g3 = Guarded("c", GuardMetadata(uncertainty=3.0))
        nested = [[g1, g2], {"x": g3}]
        info = guard_info(nested)
        assert info.uncertainty == 6.0  # 1+2+3

    def test_guard_info_empty_list(self):
        info = guard_info([])
        assert info.is_empty()

    def test_guard_info_empty_dict(self):
        info = guard_info({})
        assert info.is_empty()

    def test_guard_info_guarded_of_guarded(self):
        """Un Guarded contient un autre Guarded."""
        inner = Guarded("x", GuardMetadata(uncertainty=1.0, time_consumed=10.0))
        outer = Guarded(inner, GuardMetadata(uncertainty=0.5, time_consumed=5.0))
        info = guard_info(outer)
        # outer._metadata is the GuardMetadata passed at construction
        assert info.uncertainty == 0.5
        assert info.time_consumed == 5.0

    def test_guard_info_of_guard_list(self):
        """guard_info sur un Guarded qui encapsule une liste."""
        v1 = guard("a", GuardMetadata(uncertainty=1.0))
        v2 = guard("b", GuardMetadata(uncertainty=2.0))
        lst_g = guard([v1, v2])  # This is Guarded[list[Guarded]]
        info = guard_info(lst_g)
        # lst_g._metadata already includes aggregated children metadata
        assert info.uncertainty == 3.0

    def test_guard_info_of_guard_dataclass(self):
        """guard_info sur un Guarded qui encapsule un dataclass."""
        addr = Address(
            street=guard("Rue", GuardMetadata(uncertainty=1.0)),
            city="Paris",
            zip_code=75001,
        )
        addr_g = guard(addr, GuardMetadata(uncertainty=0.5))
        info = guard_info(addr_g)
        # parent 0.5 + street 1.0 + city 0 + zip 0 = 1.5
        assert info.uncertainty == 1.5
