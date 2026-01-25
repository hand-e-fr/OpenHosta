import pytest
from typing import List, Dict, Set, Tuple, Optional, Union
from OpenHosta.guarded.resolver import TypeResolver, type_returned_data
from OpenHosta.guarded.subclassablescalars import GuardedInt, GuardedUtf8, GuardedFloat
from OpenHosta.guarded.subclassablecollections import GuardedList, GuardedDict, GuardedSet, GuardedTuple
from OpenHosta.guarded.subclassablewithproxy import GuardedBool, GuardedNone


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
        assert issubclass(resolved, GuardedList)
        assert resolved._item_type == GuardedInt
    
    def test_resolve_dict_str_int(self):
        """Test resolving Dict[str, int]."""
        resolved = TypeResolver.resolve(Dict[str, int])
        assert issubclass(resolved, GuardedDict)
        assert resolved._key_type == GuardedUtf8
        assert resolved._value_type == GuardedInt
    
    def test_resolve_optional(self):
        """Test resolving Optional[int]."""
        resolved = TypeResolver.resolve(Optional[int])
        # Optional[int] is Union[int, None], should resolve to GuardedInt
        assert resolved == GuardedInt
    
    def test_resolve_union(self):
        """Test resolving Union types."""
        resolved = TypeResolver.resolve(Union[int, str])
        # Should fallback to first type for now, or use GuardedUnion if implemented
        assert resolved == GuardedInt or "Union" in str(resolved)
    
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


class TestComplexityGenericResolution:
    """Test resolution of complex nested generics."""

    def test_resolve_list_dict(self):
        """Test resolving List[Dict[str, int]]."""
        resolved = TypeResolver.resolve(List[Dict[str, int]])
        assert issubclass(resolved, GuardedList)
        item_type = resolved._item_type
        assert issubclass(item_type, GuardedDict)
        assert item_type._key_type == GuardedUtf8
        assert item_type._value_type == GuardedInt

    def test_resolve_tuple_int_str(self):
        """Test resolving Tuple[int, str]."""
        resolved = TypeResolver.resolve(Tuple[int, str])
        assert issubclass(resolved, GuardedTuple)
        assert resolved._item_types == (GuardedInt, GuardedUtf8)


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


class TestTypeResolverLiteralAndCustomTypes:
    """Test Literal and custom GuardedPrimitive types."""
    
    def test_resolve_literal(self):
        """Test resolving Literal type."""
        from typing import Literal
        
        resolved = TypeResolver.resolve(Literal["a", "b", "c"])
        # Should now return a GuardedLiteral (dynamic class)
        assert "Literal" in str(resolved) or resolved.__name__.startswith("Literal")
    
    def test_resolve_literal_int(self):
        """Test resolving Literal with integers."""
        from typing import Literal
        
        resolved = TypeResolver.resolve(Literal[1, 2, 3])
        # Should return a GuardedLiteral based on GuardedInt
        assert "Literal" in str(resolved) or resolved.__name__.startswith("Literal")
    
    def test_resolve_custom_guarded_type(self):
        """Test resolving custom GuardedPrimitive subclass."""
        from OpenHosta.guarded.subclassablescalars import GuardedUtf8
        from OpenHosta.guarded.primitives import GuardedPrimitive, UncertaintyLevel
        from OpenHosta.guarded.constants import Tolerance
        from typing import Tuple, Optional, Any
        import re
        
        # Create a custom type similar to CorporateEmail
        class CorporateEmail(GuardedUtf8):
            """Email d'entreprise."""
            
            @classmethod
            def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
                if not isinstance(value, str):
                    return UncertaintyLevel(Tolerance.ANYTHING), value, "Not a string"
                
                if re.match(r"^[a-z]+\.[a-z]+@mycorp\.com$", value):
                    return UncertaintyLevel(Tolerance.STRICT), value, None
                
                return UncertaintyLevel(Tolerance.ANYTHING), value, "Invalid format"
        
        # Test that custom type resolves to itself
        resolved = TypeResolver.resolve(CorporateEmail)
        assert resolved == CorporateEmail
    
    def test_resolve_dict_with_custom_type(self):
        """Test resolving Dict[str, CustomGuardedType]."""
        from OpenHosta.guarded.subclassablescalars import GuardedUtf8
        from OpenHosta.guarded.primitives import GuardedPrimitive, UncertaintyLevel
        from OpenHosta.guarded.constants import Tolerance
        from typing import Tuple, Optional, Any
        import re
        
        # Create a custom type
        class CorporateEmail(GuardedUtf8):
            """Email d'entreprise."""
            
            @classmethod
            def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
                if not isinstance(value, str):
                    return UncertaintyLevel(Tolerance.ANYTHING), value, "Not a string"
                
                if re.match(r"^[a-z]+\.[a-z]+@mycorp\.com$", value):
                    return UncertaintyLevel(Tolerance.STRICT), value, None
                
                return UncertaintyLevel(Tolerance.ANYTHING), value, "Invalid format"
        
        # Test Dict[str, CorporateEmail]
        resolved = TypeResolver.resolve(Dict[str, CorporateEmail])
        
        # Should return GuardedDict parameterized with GuardedUtf8 and CorporateEmail
        assert issubclass(resolved, GuardedDict)
        assert resolved._key_type == GuardedUtf8
        assert resolved._value_type == CorporateEmail
    
    def test_resolve_list_with_custom_type(self):
        """Test resolving List[CustomGuardedType]."""
        from OpenHosta.guarded.subclassablescalars import GuardedUtf8
        from OpenHosta.guarded.primitives import GuardedPrimitive, UncertaintyLevel
        from OpenHosta.guarded.constants import Tolerance
        from typing import Tuple, Optional, Any
        import re
        
        # Create a custom type
        class CorporateEmail(GuardedUtf8):
            """Email d'entreprise."""
            
            @classmethod
            def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
                if not isinstance(value, str):
                    return UncertaintyLevel(Tolerance.ANYTHING), value, "Not a string"
                
                if re.match(r"^[a-z]+\.[a-z]+@mycorp\.com$", value):
                    return UncertaintyLevel(Tolerance.STRICT), value, None
                
                return UncertaintyLevel(Tolerance.ANYTHING), value, "Invalid format"
        
        # Test List[CorporateEmail]
        resolved = TypeResolver.resolve(List[CorporateEmail])
        
        # Should return GuardedList parameterized with CorporateEmail
        assert issubclass(resolved, GuardedList)
        assert resolved._item_type == CorporateEmail
    
    def test_type_returned_data_with_custom_type(self):
        """Test type_returned_data with custom GuardedPrimitive."""
        from OpenHosta.guarded.subclassablescalars import GuardedUtf8
        from OpenHosta.guarded.primitives import GuardedPrimitive, UncertaintyLevel
        from OpenHosta.guarded.constants import Tolerance
        from typing import Tuple, Optional, Any
        import re
        
        # Create a custom type
        class CorporateEmail(GuardedUtf8):
            """Email d'entreprise."""
            
            @classmethod
            def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
                if not isinstance(value, str):
                    return UncertaintyLevel(Tolerance.ANYTHING), value, "Not a string"
                
                if re.match(r"^[a-z]+\.[a-z]+@mycorp\.com$", value):
                    return UncertaintyLevel(Tolerance.STRICT), value, None
                
                return UncertaintyLevel(Tolerance.ANYTHING), value, "Invalid format"
        
        # Test conversion
        result = type_returned_data("marie.dupont@mycorp.com", CorporateEmail)
        
        # Should be a CorporateEmail instance
        assert isinstance(result, CorporateEmail)
        assert str(result) == "marie.dupont@mycorp.com"
        assert result.uncertainty == Tolerance.STRICT
