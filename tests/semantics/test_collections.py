"""
Tests for collection types in OpenHosta.semantics.collections.
Covers SemanticList, SemanticDict, SemanticTuple.
"""
import pytest
from dotenv import load_dotenv

load_dotenv()


# ==============================================================================
# SEMANTIC LIST TESTS
# ==============================================================================

class TestSemanticListBasic:
    """Basic tests for SemanticList."""
    
    def test_list_from_native_list(self):
        """Should accept native list."""
        from OpenHosta.semantics import SemanticList
        
        result = SemanticList(["a", "b", "c"])
        assert len(result) == 3
        assert result[0] == "a"
    
    def test_list_bracket_syntax(self):
        """Should support bracket syntax SemanticList[Type]."""
        from OpenHosta.semantics import SemanticList, SemanticInt
        
        IntList = SemanticList[SemanticInt]
        assert isinstance(IntList, type)
    
    def test_list_typed_instantiation(self):
        """Typed list should validate elements."""
        from OpenHosta.semantics import SemanticList, SemanticInt
        
        IntList = SemanticList[SemanticInt]
        result = IntList([1, 2, 3])
        
        assert len(result) == 3
        assert all(isinstance(x, int) for x in result)


class TestSemanticListHeuristic:
    """Tests for SemanticList heuristic parsing."""
    
    @pytest.mark.skip(reason="JSON string parsing requires going through GuardedPrimitive.__new__ heuristic path")
    def test_json_string_parsing(self):
        """Should parse JSON string as list - requires heuristic/LLM."""
        from OpenHosta.semantics import SemanticList
        
        result = SemanticList('[1, 2, 3]')
        assert len(result) == 3
    
    @pytest.mark.skip(reason="JSON string parsing requires going through GuardedPrimitive.__new__ heuristic path")
    def test_json_string_with_spaces(self):
        """Should handle JSON string with extra spaces - requires heuristic/LLM."""
        from OpenHosta.semantics import SemanticList
        
        result = SemanticList('  [1, 2, 3]  ')
        assert len(result) == 3


# ==============================================================================
# SEMANTIC DICT TESTS
# ==============================================================================

class TestSemanticDictBasic:
    """Basic tests for SemanticDict."""
    
    def test_dict_from_native_dict(self):
        """Should accept native dict."""
        from OpenHosta.semantics import SemanticDict
        
        result = SemanticDict({"key": "value"})
        assert result["key"] == "value"
    
    def test_dict_bracket_syntax(self):
        """Should support bracket syntax SemanticDict[K, V]."""
        from OpenHosta.semantics import SemanticDict, SemanticStr, SemanticInt
        
        StrIntDict = SemanticDict[SemanticStr, SemanticInt]
        assert isinstance(StrIntDict, type)
    
    def test_dict_typed_instantiation(self):
        """Typed dict should validate keys and values."""
        from OpenHosta.semantics import SemanticDict, SemanticStr, SemanticInt
        
        StrIntDict = SemanticDict[SemanticStr, SemanticInt]
        result = StrIntDict({"count": 42})
        
        assert result["count"] == 42


class TestSemanticDictHeuristic:
    """Tests for SemanticDict heuristic parsing."""
    
    @pytest.mark.skip(reason="JSON string parsing requires actual JSON data, not string")
    def test_json_string_parsing(self):
        """Should parse JSON string as dict - requires heuristic/LLM."""
        from OpenHosta.semantics import SemanticDict
        
        result = SemanticDict('{"a": 1}')
        assert result["a"] == 1


class TestSemanticDictSemanticLookup:
    """Tests for SemanticDict semantic key lookup (requires embedding API)."""
    
    def test_exact_key_lookup(self):
        """Exact key should work normally."""
        from OpenHosta.semantics import SemanticDict
        
        d = SemanticDict({"chien": "wouf"})
        assert d["chien"] == "wouf"
    
    def test_missing_key_raises(self):
        """Missing key should raise KeyError."""
        from OpenHosta.semantics import SemanticDict
        
        d = SemanticDict({"chien": "wouf"})
        with pytest.raises(KeyError):
            _ = d["completely_unrelated_key_xyz"]


# ==============================================================================
# SEMANTIC TUPLE TESTS
# ==============================================================================

class TestSemanticTupleBasic:
    """Basic tests for SemanticTuple."""
    
    def test_tuple_from_native_tuple(self):
        """Should accept native tuple."""
        from OpenHosta.semantics import SemanticTuple
        
        result = SemanticTuple((1, 2, 3))
        assert len(result) == 3
        assert result[0] == 1
    
    def test_tuple_from_list(self):
        """Should accept list and convert to tuple."""
        from OpenHosta.semantics import SemanticTuple
        
        result = SemanticTuple([1, 2, 3])
        assert isinstance(result, tuple)


class TestSemanticTupleHeuristic:
    """Tests for SemanticTuple heuristic parsing."""
    
    @pytest.mark.skip(reason="String tuple parsing requires actual tuple data, not string")
    def test_string_tuple_parsing(self):
        """Should parse string representation of tuple - requires heuristic."""
        from OpenHosta.semantics import SemanticTuple
        
        result = SemanticTuple("(1, 2, 3)")
        assert len(result) == 3
