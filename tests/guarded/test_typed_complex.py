"""Tests for complex typed collections and unions."""

import pytest
from typing import List, Tuple, Dict, Union, Literal
from OpenHosta.guarded.resolver import TypeResolver, type_returned_data
from OpenHosta.guarded.subclassableliterals import GuardedLiteral, guarded_literal
from OpenHosta.guarded.subclassableunions import GuardedUnion, guarded_union
from OpenHosta.guarded.subclassablescalars import GuardedInt, GuardedUtf8, GuardedFloat
from OpenHosta.guarded.constants import Tolerance


class TestGuardedLiteral:
    """Tests for GuardedLiteral type."""
    
    def test_literal_str_basic(self):
        Color = guarded_literal("red", "green", "blue")
        c = Color("red")
        assert c == "red"
        assert c.uncertainty == Tolerance.STRICT

    def test_literal_str_heuristic(self):
        Color = guarded_literal("red", "green", "blue")
        # Case insensitive
        c = Color("RED")
        assert c == "red"
        assert c.uncertainty == Tolerance.PRECISE
        # With spaces
        c = Color("  blue  ")
        assert c == "blue"
        assert c.uncertainty == Tolerance.PRECISE

    def test_literal_int(self):
        Level = guarded_literal(1, 2, 3)
        l = Level(2)
        assert l == 2
        # From string
        l2 = Level("3")
        assert l2 == 3
        assert l2.uncertainty == Tolerance.PRECISE

    def test_literal_failure(self):
        Level = guarded_literal(1, 2, 3)
        with pytest.raises(ValueError):
            Level(5)


class TestTypedCollections:
    """Tests for typed collections resolution and conversion."""
    
    def test_list_int_conversion(self):
        res = type_returned_data(["1", "2", "3"], List[int])
        assert res == [1, 2, 3]
        assert all(isinstance(x, int) for x in res)

    def test_tuple_fixed_length(self):
        res = type_returned_data(["10", "hello", "3.14"], Tuple[int, str, float])
        assert res == (10, "hello", 3.14)
        assert isinstance(res[0], int)
        assert isinstance(res[1], str)
        assert isinstance(res[2], float)

    def test_dict_typed(self):
        res = type_returned_data({"a": "1", "b": "2"}, Dict[str, int])
        assert res == {"a": 1, "b": 2}
        assert isinstance(res["a"], int)


class TestGuardedUnion:
    """Tests for GuardedUnion type."""
    
    def test_union_int_str(self):
        MyUnion = guarded_union(GuardedInt, GuardedUtf8)
        
        # Test int match
        u1 = MyUnion("42")
        assert isinstance(u1, int)
        assert u1 == 42
        
        # Test str match (when int fails)
        u2 = MyUnion("hello")
        assert isinstance(u2, str)
        assert u2 == "hello"

    def test_union_precedence(self):
        # Even if both could match, preference to order or better confidence
        MyUnion = guarded_union(GuardedFloat, GuardedInt)
        u = MyUnion("42")
        # In our implementation, GuardedFloat comes first and succeeds
        assert isinstance(u, float)

    def test_union_complex(self):
        """Test union of complex types."""
        MyUnion = guarded_union(List[int], Dict[str, int])
        
        u1 = MyUnion("[1, 2, 3]")
        assert isinstance(u1, list)
        assert u1 == [1, 2, 3]
        
        u2 = MyUnion('{"a": 1}')
        assert isinstance(u2, dict)
        assert u2 == {"a": 1}


class TestNewScalars:
    """Tests for newer scalar types."""
    
    def test_complex(self):
        from OpenHosta.guarded.subclassablescalars import GuardedComplex
        c = GuardedComplex("1+2j")
        assert c == complex(1, 2)
        assert c.uncertainty == Tolerance.TYPE_COMPLIANT

    def test_bytes(self):
        from OpenHosta.guarded.subclassablescalars import GuardedBytes
        b = GuardedBytes("hello")
        assert b == b"hello"
        assert isinstance(b, bytes)
