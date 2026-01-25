import pytest
from typing import List, Tuple, Dict, Union, Literal
from src.OpenHosta.guarded.resolver import TypeResolver, type_returned_data
from src.OpenHosta.guarded.subclassableliterals import GuardedLiteral, guarded_literal
from src.OpenHosta.guarded.subclassableunions import GuardedUnion, guarded_union
from src.OpenHosta.guarded.subclassablescalars import GuardedInt, GuardedUtf8, GuardedFloat
from src.OpenHosta.guarded.constants import Tolerance

class TestGuardedLiteral:
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
        # Here GuardedFloat matches 42 better than GuardedUtf8 (heuristic vs heuristic)
        # But both are flexible.
        MyUnion = guarded_union(GuardedFloat, GuardedInt)
        u = MyUnion("42")
        # In our implementation, GuardedFloat comes first and succeeds
        assert isinstance(u, float)

class TestNewScalars:
    def test_complex(self):
        from src.OpenHosta.guarded.subclassablescalars import GuardedComplex
        c = GuardedComplex("1+2j")
        assert c == complex(1, 2)
        assert c.uncertainty == Tolerance.TYPE_COMPLIANT

    def test_bytes(self):
        from src.OpenHosta.guarded.subclassablescalars import GuardedBytes
        b = GuardedBytes("hello")
        assert b == b"hello"
        assert isinstance(b, bytes)
