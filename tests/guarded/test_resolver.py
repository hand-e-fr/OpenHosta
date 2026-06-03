import pytest
from typing import List, Dict, Set, Tuple, Optional, Union, Literal
from openhosta.guarded.resolver import TypeResolver, type_returned_data
from openhosta.guarded.subclassablescalars import GuardedInt, GuardedUtf8, GuardedFloat
from openhosta.guarded.subclassablecollections import GuardedList, GuardedDict, GuardedSet, GuardedTuple
from openhosta.guarded.subclassablewithproxy import GuardedBool, GuardedNone
from openhosta.guarded.subclassableunions import GuardedUnion


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
        assert issubclass(resolved, GuardedUnion)
        assert not isinstance(resolved("5"), GuardedUnion)
        assert isinstance(resolved("5"), GuardedInt)
        assert isinstance(resolved("5"), int)
    
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
        
        # Now raises TypeError instead of falling back to GuardedUtf8
        with pytest.raises(TypeError):
             TypeResolver.resolve(CustomClass)

    def test_resolve_callable(self):
        """Test resolving Callable types."""
        from typing import Callable as TypingCallable
        import collections.abc
        from openhosta.guarded.subclassablecallables import GuardedCode
        
        assert TypeResolver.resolve(TypingCallable) == GuardedCode
        assert TypeResolver.resolve(collections.abc.Callable) == GuardedCode
        assert issubclass(TypeResolver.resolve(TypingCallable[[int], str]), GuardedCode)

    def test_resolve_string_annotations(self):
        """Test resolving stringified annotations (safety net in resolver)."""
        import warnings
        from openhosta.guarded.subclassablecallables import GuardedCode
        from openhosta.guarded.subclassablescalars import GuardedInt
        
        # These should still work but now emit a deprecation warning
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            assert TypeResolver.resolve("int") == GuardedInt
            assert TypeResolver.resolve("Callable") == GuardedCode
            assert TypeResolver.resolve("typing.Callable") == GuardedCode
            assert TypeResolver.resolve("List[int]") == GuardedList
    
    def test_string_annotation_emits_warning(self):
        """Test that string annotations trigger a deprecation warning."""
        import warnings
        TypeResolver._RESOLVE_CACHE.clear()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            assert TypeResolver.resolve("int") == GuardedInt
            assert len(w) == 1
            assert "gap in upstream type resolution" in str(w[0].message)


class TestResolveAnnotationHelper:
    """Tests for _resolve_annotation — skipped: function removed in V5 (was in openhosta.core.analizer)."""

    @pytest.mark.skip(reason="V4 function _resolve_annotation no longer exists in V5")
    def test_resolve_non_string_passthrough(self):
        pass

    @pytest.mark.skip(reason="V4 function _resolve_annotation no longer exists in V5")
    def test_resolve_string_to_type(self):
        pass

    @pytest.mark.skip(reason="V4 function _resolve_annotation no longer exists in V5")
    def test_resolve_unknown_string_falls_back_to_any(self):
        pass


class TestHostaAnalyzeStringAnnotations:
    """Tests for hosta_analyze — skipped: function removed in V5 (was in openhosta.core.analizer)."""

    @pytest.mark.skip(reason="V4 function hosta_analyze no longer exists in V5")
    def test_analyze_resolves_return_type(self):
        pass

    @pytest.mark.skip(reason="V4 function hosta_analyze no longer exists in V5")
    def test_analyze_with_callable_annotation(self):
        pass


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
        assert result == True
    
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
        MyType = TypeResolver.resolve(None)
        result = MyType("None")
        assert result == None
    
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
        MyType = TypeResolver.resolve(int)
        result = MyType("42")
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
    
        # Should return a GuardedLiteral based on GuardedInt
        assert "Literal" in str(resolved) or resolved.__name__.startswith("Literal")

    def test_resolve_type_alias_pep695(self):
        """Test resolving Python 3.12+ TypeAliasType (PEP 695)."""
        import sys
        if sys.version_info < (3, 12):
            pytest.skip("TypeAliasType (PEP 695) requires Python 3.12+")
            
        from typing import Literal
        # This syntax is only valid in Python 3.12+
        # Provide Literal in the namespace for exec
        namespace = {"Literal": Literal}
        exec("type MyAlias = Literal['a', 'b']", globals(), namespace)
        MyAlias = namespace["MyAlias"]

        
        resolved = TypeResolver.resolve(MyAlias)
        assert "Literal" in str(resolved)
        assert "a" in str(resolved) and "b" in str(resolved)

    
    def test_resolve_custom_guarded_type(self):
        """Test resolving custom GuardedPrimitive subclass."""
        from openhosta.guarded.subclassablescalars import GuardedUtf8
        from openhosta.guarded.primitives import GuardedPrimitive, UncertaintyLevel
        from openhosta.guarded.constants import Tolerance
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
        from openhosta.guarded.subclassablescalars import GuardedUtf8
        from openhosta.guarded.primitives import GuardedPrimitive, UncertaintyLevel
        from openhosta.guarded.constants import Tolerance
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
        from openhosta.guarded.subclassablescalars import GuardedUtf8
        from openhosta.guarded.primitives import GuardedPrimitive, UncertaintyLevel
        from openhosta.guarded.constants import Tolerance
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
        from openhosta.guarded.subclassablescalars import GuardedUtf8
        from openhosta.guarded.primitives import GuardedPrimitive, UncertaintyLevel
        from openhosta.guarded.constants import Tolerance
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
        result = CorporateEmail("marie.dupont@mycorp.com")
        assert isinstance(result, CorporateEmail) 
        assert result.uncertainty == Tolerance.STRICT
        
        result = type_returned_data("marie.dupont@mycorp.com", CorporateEmail)
        # Should be a CorporateEmail instance
        assert isinstance(result, str)
        assert str(result) == "marie.dupont@mycorp.com"


class TestNiceTypeWithNameGuardedT:
    """Test that nice_type_name properly unwraps Guarded[T] to display the inner type."""

    def test_guarded_class_returns_class_name(self):
        """Guarded[SomeClass] should display as the class name, not Guarded[SomeClass]."""
        from openhosta.guarded.type_hints import nice_type_name
        from openhosta import Guarded

        class Sentiment:
            pass

        result = nice_type_name(Guarded[Sentiment])
        assert result == "Sentiment", f"Expected 'Sentiment', got '{result}'"

    def test_guarded_builtin_returns_builtin_name(self):
        """Guarded[str], Guarded[int], etc. should display as the builtin name."""
        from openhosta.guarded.type_hints import nice_type_name
        from openhosta import Guarded

        assert nice_type_name(Guarded[str]) == "str"
        assert nice_type_name(Guarded[int]) == "int"
        assert nice_type_name(Guarded[float]) == "float"
        assert nice_type_name(Guarded[bool]) == "bool"

    def test_guarded_generic_returns_inner_generic(self):
        """Guarded[List[int]] should display as List[int]."""
        from openhosta.guarded.type_hints import nice_type_name
        from openhosta import Guarded

        result = nice_type_name(Guarded[List[int]])
        assert result == "List[int]", f"Expected 'List[int]', got '{result}'"

    def test_guarded_nested_generic(self):
        """Guarded[Dict[str, int]] should display as Dict[str, int]."""
        from openhosta.guarded.type_hints import nice_type_name
        from openhosta import Guarded

        result = nice_type_name(Guarded[Dict[str, int]])
        assert result == "Dict[str, int]", f"Expected 'Dict[str, int]', got '{result}'"

    def test_guarded_optional(self):
        """Guarded[Optional[str]] should display as Optional[str]."""
        from openhosta.guarded.type_hints import nice_type_name
        from openhosta import Guarded

        result = nice_type_name(Guarded[Optional[str]])
        assert result == "Optional[str]", f"Expected 'Optional[str]', got '{result}'"

    def test_regular_types_unchanged(self):
        """Non-Guarded types should still work normally."""
        from openhosta.guarded.type_hints import nice_type_name

        assert nice_type_name(str) == "str"
        assert nice_type_name(int) == "int"
        assert nice_type_name(None) == "Any"

    def test_regular_generics_unchanged(self):
        """Non-Guarded generic types should still work normally."""
        from openhosta.guarded.type_hints import nice_type_name

        assert nice_type_name(List[int]) == "List[int]"
        assert nice_type_name(Dict[str, int]) == "Dict[str, int]"


class TestGenericArityValidation:
    """Test that malformed generic annotations raise TypeError at resolve time."""

    def test_dict_missing_value_type(self):
        """dict[list[str]] should raise TypeError (only 1 arg, needs 2)."""
        with pytest.raises(TypeError, match="requires exactly 2"):
            TypeResolver.resolve(dict[list[str]])

    def test_dict_three_args(self):
        """dict[str, int, bool] should raise TypeError (too many args)."""
        with pytest.raises(TypeError, match="requires exactly 2"):
            TypeResolver.resolve(dict[str, int, bool])

    def test_list_two_args(self):
        """list[int, str] should raise TypeError (too many args)."""
        with pytest.raises(TypeError, match="requires exactly 1"):
            TypeResolver.resolve(list[int, str])

    def test_set_two_args(self):
        """set[int, str] should raise TypeError (too many args)."""
        with pytest.raises(TypeError, match="requires exactly 1"):
            TypeResolver.resolve(set[int, str])

    def test_dict_valid_still_works(self):
        """Ensure valid dict[str, list[str]] still resolves correctly."""
        resolved = TypeResolver.resolve(dict[str, list[str]])
        assert issubclass(resolved, GuardedDict)
        assert resolved._key_type == GuardedUtf8
        assert issubclass(resolved._value_type, GuardedList)

    def test_list_valid_still_works(self):
        """Ensure valid list[str] still resolves correctly."""
        resolved = TypeResolver.resolve(list[str])
        assert issubclass(resolved, GuardedList)
        assert resolved._item_type == GuardedUtf8
