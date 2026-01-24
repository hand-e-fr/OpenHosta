"""
Tests for TypeResolver in OpenHosta.semantics.resolver.
Verifies resolution of Python type annotations to SemanticTypes.
"""
import pytest
from typing import List, Dict, Set, Tuple, Optional, Union
from dotenv import load_dotenv

load_dotenv()


class TestTypeResolverPrimitives:
    """Tests for primitive type resolution."""
    
    def test_resolve_int(self):
        """int should resolve to SemanticInt."""
        from OpenHosta.semantics import SemanticType, SemanticInt
        from OpenHosta.guarded.resolver import TypeResolver
        
        resolved = TypeResolver.resolve(int)
        assert resolved is SemanticInt
    
    def test_resolve_str(self):
        """str should resolve to SemanticStr."""
        from OpenHosta.semantics import SemanticStr
        from OpenHosta.guarded.resolver import TypeResolver
        
        resolved = TypeResolver.resolve(str)
        assert resolved is SemanticStr
    
    def test_resolve_float(self):
        """float should resolve to SemanticFloat."""
        from OpenHosta.semantics import SemanticFloat
        from OpenHosta.guarded.resolver import TypeResolver
        
        resolved = TypeResolver.resolve(float)
        assert resolved is SemanticFloat
    
    def test_resolve_bool(self):
        """bool should resolve to SemanticBool."""
        from OpenHosta.semantics import SemanticBool
        from OpenHosta.guarded.resolver import TypeResolver
        
        resolved = TypeResolver.resolve(bool)
        assert resolved is SemanticBool


class TestTypeResolverIdempotence:
    """Tests for idempotence - SemanticTypes should pass through unchanged."""
    
    def test_semantic_int_passthrough(self):
        """SemanticInt should resolve to itself."""
        from OpenHosta.semantics import SemanticInt
        from OpenHosta.guarded.resolver import TypeResolver
        
        resolved = TypeResolver.resolve(SemanticInt)
        assert resolved is SemanticInt
    
    def test_semantic_str_passthrough(self):
        """SemanticStr should resolve to itself."""
        from OpenHosta.semantics import SemanticStr
        from OpenHosta.guarded.resolver import TypeResolver
        
        resolved = TypeResolver.resolve(SemanticStr)
        assert resolved is SemanticStr


class TestTypeResolverGenerics:
    """Tests for generic type resolution."""
    
    def test_resolve_list_int(self):
        """List[int] should resolve to SemanticList[SemanticInt]."""
        from OpenHosta.guarded.resolver import TypeResolver
        
        resolved = TypeResolver.resolve(List[int])
        # The resolved class should be a SemanticList variant
        assert hasattr(resolved, '_inner_semantic_type')
    
    def test_resolve_dict_str_int(self):
        """Dict[str, int] should resolve to SemanticDict."""
        from OpenHosta.guarded.resolver import TypeResolver
        
        resolved = TypeResolver.resolve(Dict[str, int])
        assert hasattr(resolved, '_key_semantic_type')
        assert hasattr(resolved, '_val_semantic_type')
    
    def test_resolve_set(self):
        """Set[str] should resolve to SemanticSet variant."""
        from OpenHosta.guarded.resolver import TypeResolver
        
        resolved = TypeResolver.resolve(Set[str])
        # Should be a function result or class with SemanticSet behavior
        assert resolved is not None
    
    def test_resolve_tuple_fixed(self):
        """Tuple[int, str] should resolve to fixed tuple."""
        from OpenHosta.guarded.resolver import TypeResolver
        
        resolved = TypeResolver.resolve(Tuple[int, str])
        assert hasattr(resolved, '_item_types')


class TestTypeResolverOptionalUnion:
    """Tests for Optional and Union resolution."""
    
    def test_resolve_optional_int(self):
        """Optional[int] should resolve (filtering None)."""
        from OpenHosta.semantics import SemanticInt
        from OpenHosta.guarded.resolver import TypeResolver
        
        resolved = TypeResolver.resolve(Optional[int])
        # Optional[int] = Union[int, None], should resolve to SemanticInt
        assert resolved is SemanticInt
    
    def test_resolve_union_single(self):
        """Union with single type (after NoneType filter) should resolve."""
        from OpenHosta.semantics import SemanticStr
        from OpenHosta.guarded.resolver import TypeResolver
        
        resolved = TypeResolver.resolve(Union[str, None])
        assert resolved is SemanticStr


class TestTypeResolverFallback:
    """Tests for fallback behavior."""
    
    def test_unknown_type_fallback_to_str(self):
        """Unknown types should fallback to SemanticStr."""
        from OpenHosta.semantics import SemanticStr
        from OpenHosta.guarded.resolver import TypeResolver
        
        class CustomClass:
            pass
        
        resolved = TypeResolver.resolve(CustomClass)
        assert resolved is SemanticStr
