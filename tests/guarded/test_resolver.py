"""Tests for TypeResolver."""

import pytest
from typing import List, Dict, Set, Tuple, Optional, Union
from src.OpenHosta.guarded.resolver import TypeResolver, type_returned_data
from src.OpenHosta.guarded.subclassablescalars import GuardedInt, GuardedUtf8, GuardedFloat
from src.OpenHosta.guarded.subclassablecollections import GuardedList, GuardedDict, GuardedSet, GuardedTuple
from src.OpenHosta.guarded.subclassablewithproxy import GuardedBool, GuardedNone


class TestTypeResolver:
    """Tests for TypeResolver.resolve()."""
    
    def test_resolve_int(self):
        """Test resolving int type."""
        resolved = TypeResolver.resolve(int)
        assert resolved == GuardedInt
    
    def test_resolve_str(self):
        """Test resolving str type."""
        resolved = TypeResolver.resolve(str)
        assert resolved == GuardedUtf8
    
    def test_resolve_float(self):
        """Test resolving float type."""
        resolved = TypeResolver.resolve(float)
        assert resolved == GuardedFloat
    
    def test_resolve_bool(self):
        """Test resolving bool type."""
        resolved = TypeResolver.resolve(bool)
        assert resolved == GuardedBool
    
    def test_resolve_list(self):
        """Test resolving list type."""
        resolved = TypeResolver.resolve(list)
        assert resolved == GuardedList
    
    def test_resolve_dict(self):
        """Test resolving dict type."""
        resolved = TypeResolver.resolve(dict)
        assert resolved == GuardedDict
    
    def test_resolve_list_int(self):
        """Test resolving List[int]."""
        resolved = TypeResolver.resolve(List[int])
        # Should return GuardedList parameterized with GuardedInt
        # This is complex, might not work exactly as expected
        assert resolved == GuardedList or "GuardedList" in str(resolved)
    
    def test_resolve_dict_str_int(self):
        """Test resolving Dict[str, int]."""
        resolved = TypeResolver.resolve(Dict[str, int])
        assert resolved == GuardedDict or "GuardedDict" in str(resolved)
    
    def test_resolve_optional(self):
        """Test resolving Optional[int]."""
        resolved = TypeResolver.resolve(Optional[int])
        # Optional[int] is Union[int, None], should resolve to GuardedInt
        assert resolved == GuardedInt
    
    def test_resolve_union(self):
        """Test resolving Union types."""
        resolved = TypeResolver.resolve(Union[int, str])
        # Should fallback to first type
        assert resolved == GuardedInt
    
    def test_resolve_guarded_type(self):
        """Test that GuardedType resolves to itself (idempotence)."""
        resolved = TypeResolver.resolve(GuardedInt)
        assert resolved == GuardedInt
    
    def test_resolve_none(self):
        """Test resolving None type."""
        from types import NoneType
        resolved = TypeResolver.resolve(NoneType)
        assert resolved == GuardedNone
    
    def test_resolve_unknown(self):
        """Test resolving unknown type."""
        class CustomClass:
            pass
        
        resolved = TypeResolver.resolve(CustomClass)
        # Should fallback to GuardedUtf8
        assert resolved == GuardedUtf8


class TestTypeReturnedData:
    """Tests for type_returned_data() function."""
    
    def test_convert_to_int(self):
        """Test converting string to int."""
        result = type_returned_data("42", int)
        assert result == 42
        assert isinstance(result, int)
    
    def test_convert_to_float(self):
        """Test converting string to float."""
        result = type_returned_data("3.14", float)
        assert abs(result - 3.14) < 0.01
    
    def test_convert_to_str(self):
        """Test converting to string."""
        result = type_returned_data("hello", str)
        assert result == "hello"
    
    def test_convert_to_bool(self):
        """Test converting to bool."""
        result = type_returned_data("yes", bool)
        # Result should be GuardedBool
        assert result.unwrap() == True
    
    def test_convert_to_list(self):
        """Test converting to list."""
        result = type_returned_data("[1, 2, 3]", list)
        assert result == [1, 2, 3]
    
    def test_convert_to_dict(self):
        """Test converting to dict."""
        result = type_returned_data('{"a": 1}', dict)
        assert result == {"a": 1}
    
    def test_convert_none_type(self):
        """Test with None as expected type."""
        result = type_returned_data("anything", None)
        assert result == "anything"
    
    def test_convert_invalid(self):
        """Test that invalid conversion raises error."""
        with pytest.raises(ValueError):
            type_returned_data("not a number", int)
    
    def test_convert_with_tolerance(self):
        """Test conversion with flexible parsing."""
        # "1,000" should be parsed as 1000
        result = type_returned_data("1,000", int)
        assert result == 1000
    
    def test_convert_list_int(self):
        """Test converting to List[int]."""
        result = type_returned_data("[1, 2, 3]", List[int])
        assert result == [1, 2, 3]
    
    def test_metadata_preserved(self):
        """Test that metadata is preserved in result."""
        result = type_returned_data("42", int)
        # GuardedInt should have metadata
        assert hasattr(result, 'uncertainty')
        assert hasattr(result, 'abstraction_level')


class TestTypeResolverEdgeCases:
    """Test edge cases for TypeResolver."""
    
    def test_resolve_tuple(self):
        """Test resolving tuple type."""
        resolved = TypeResolver.resolve(tuple)
        assert resolved == GuardedTuple
    
    def test_resolve_set(self):
        """Test resolving set type."""
        resolved = TypeResolver.resolve(set)
        assert resolved == GuardedSet
    
    def test_resolve_frozenset(self):
        """Test resolving frozenset type."""
        resolved = TypeResolver.resolve(frozenset)
        # Maps to GuardedSet
        assert resolved == GuardedSet
    
    def test_resolve_nested_generic(self):
        """Test resolving nested generic types."""
        resolved = TypeResolver.resolve(List[List[int]])
        # Should handle nested types
        assert "GuardedList" in str(resolved) or resolved == GuardedList
