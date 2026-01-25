"""Tests for GuardedList, GuardedDict, GuardedSet, GuardedTuple."""

import pytest
from src.OpenHosta.guarded.constants import Tolerance
from src.OpenHosta.guarded.subclassablecollections import (
    GuardedList, GuardedDict, GuardedSet, GuardedTuple
)


class TestGuardedList:
    """Tests for GuardedList type."""
    
    def test_native_list(self):
        """Test with native list."""
        lst = GuardedList([1, 2, 3])
        assert lst == [1, 2, 3]
        assert lst.uncertainty == Tolerance.STRICT
    
    def test_from_tuple(self):
        """Test conversion from tuple."""
        lst = GuardedList((1, 2, 3))
        assert lst == [1, 2, 3]
        assert lst.uncertainty <= Tolerance.PRECISE
    
    def test_from_set(self):
        """Test conversion from set."""
        lst = GuardedList({1, 2, 3})
        assert len(lst) == 3
        assert set(lst) == {1, 2, 3}
    
    def test_from_json_string(self):
        """Test parsing from JSON string."""
        lst = GuardedList("[1, 2, 3]")
        assert lst == [1, 2, 3]
        assert lst.uncertainty <= Tolerance.FLEXIBLE
    
    def test_from_csv_string(self):
        """Test parsing from CSV string."""
        lst = GuardedList("1,2,3")
        assert len(lst) == 3
        assert lst == ["1", "2", "3"]
    
    def test_list_operations(self):
        """Test that list operations work."""
        lst = GuardedList([1, 2, 3])
        
        lst.append(4)
        assert lst == [1, 2, 3, 4]
        
        lst.extend([5, 6])
        assert lst == [1, 2, 3, 4, 5, 6]
        
        assert lst[0] == 1
        assert len(lst) == 6
    
    def test_empty_list(self):
        """Test with empty list."""
        lst = GuardedList([])
        assert lst == []
        assert len(lst) == 0


class TestGuardedDict:
    """Tests for GuardedDict type."""
    
    def test_native_dict(self):
        """Test with native dict."""
        d = GuardedDict({"a": 1, "b": 2})
        assert d == {"a": 1, "b": 2}
        assert d.uncertainty == Tolerance.STRICT
    
    def test_from_json_string(self):
        """Test parsing from JSON string."""
        d = GuardedDict('{"a": 1, "b": 2}')
        assert d == {"a": 1, "b": 2}
        assert d.uncertainty <= Tolerance.FLEXIBLE
    
    def test_from_python_repr(self):
        """Test parsing from Python repr."""
        d = GuardedDict("{'a': 1, 'b': 2}")
        assert d == {"a": 1, "b": 2}
    
    def test_dict_operations(self):
        """Test that dict operations work."""
        d = GuardedDict({"a": 1})
        
        d["b"] = 2
        assert d == {"a": 1, "b": 2}
        
        assert "a" in d
        assert d.get("c") is None
        assert list(d.keys()) == ["a", "b"]
    
    def test_empty_dict(self):
        """Test with empty dict."""
        d = GuardedDict({})
        assert d == {}
        assert len(d) == 0


class TestGuardedSet:
    """Tests for GuardedSet type."""
    
    def test_native_set(self):
        """Test with native set."""
        s = GuardedSet({1, 2, 3})
        assert s == {1, 2, 3}
        assert s.uncertainty == Tolerance.STRICT
    
    def test_from_list(self):
        """Test conversion from list."""
        s = GuardedSet([1, 2, 2, 3])
        assert s == {1, 2, 3}
        assert s.uncertainty <= Tolerance.PRECISE
    
    def test_from_frozenset(self):
        """Test conversion from frozenset."""
        s = GuardedSet(frozenset({1, 2, 3}))
        assert s == {1, 2, 3}
    
    def test_from_csv_string(self):
        """Test parsing from CSV string."""
        s = GuardedSet("1,2,3")
        assert len(s) == 3
    
    def test_set_operations(self):
        """Test that set operations work."""
        s = GuardedSet({1, 2, 3})
        
        s.add(4)
        assert 4 in s
        
        s.remove(1)
        assert 1 not in s
        
        assert len(s) == 3
    
    def test_uniqueness(self):
        """Test that sets maintain uniqueness."""
        s = GuardedSet([1, 1, 2, 2, 3, 3])
        assert len(s) == 3
        assert s == {1, 2, 3}


class TestGuardedTuple:
    """Tests for GuardedTuple type."""
    
    def test_native_tuple(self):
        """Test with native tuple."""
        t = GuardedTuple((1, 2, 3))
        assert t == (1, 2, 3)
        assert t.uncertainty == Tolerance.STRICT
    
    def test_from_list(self):
        """Test conversion from list."""
        t = GuardedTuple([1, 2, 3])
        assert t == (1, 2, 3)
        assert t.uncertainty <= Tolerance.PRECISE
    
    def test_from_string(self):
        """Test parsing from string."""
        t = GuardedTuple("(1, 2, 3)")
        assert t == (1, 2, 3)
    
    def test_from_csv_string(self):
        """Test parsing from CSV string."""
        t = GuardedTuple("1,2,3")
        assert len(t) == 3
    
    def test_tuple_immutability(self):
        """Test that tuples are immutable."""
        t = GuardedTuple((1, 2, 3))
        
        with pytest.raises(TypeError):
            t[0] = 10
    
    def test_tuple_indexing(self):
        """Test tuple indexing."""
        t = GuardedTuple((1, 2, 3))
        
        assert t[0] == 1
        assert t[-1] == 3
        assert t[1:] == (2, 3)
    
    def test_empty_tuple(self):
        """Test with empty tuple."""
        t = GuardedTuple(())
        assert t == ()
        assert len(t) == 0


class TestCollectionMetadata:
    """Test that collections preserve metadata."""
    
    def test_list_metadata(self):
        """Test GuardedList metadata."""
        lst = GuardedList([1, 2, 3])
        assert hasattr(lst, 'uncertainty')
        assert hasattr(lst, 'abstraction_level')
        assert hasattr(lst, 'unwrap')
    
    def test_dict_metadata(self):
        """Test GuardedDict metadata."""
        d = GuardedDict({"a": 1})
        assert hasattr(d, 'uncertainty')
        assert hasattr(d, 'abstraction_level')
    
    def test_metadata_after_operations(self):
        """Test that metadata persists after operations."""
        lst = GuardedList([1, 2])
        original_uncertainty = lst.uncertainty
        
        lst.append(3)
        
        # Metadata should still be accessible
        assert hasattr(lst, 'uncertainty')
        assert lst.uncertainty == original_uncertainty


class TestCollectionEdgeCases:
    """Test edge cases for collections."""
    
    def test_nested_structures(self):
        """Test nested collections."""
        lst = GuardedList([[1, 2], [3, 4]])
        assert lst == [[1, 2], [3, 4]]
        
        d = GuardedDict({"nested": {"a": 1}})
        assert d == {"nested": {"a": 1}}
    
    def test_mixed_types(self):
        """Test collections with mixed types."""
        lst = GuardedList([1, "two", 3.0, None])
        assert len(lst) == 4
        
        d = GuardedDict({"int": 1, "str": "hello", "list": [1, 2]})
        assert len(d) == 3
    
    def test_invalid_json(self):
        """Test handling of invalid JSON."""
        with pytest.raises(ValueError):
            GuardedDict("{invalid json}")
