"""Tests for GuardedEnum."""

import pytest
from OpenHosta.guarded.constants import Tolerance
from OpenHosta.guarded.subclassableclasses import guarded_enum
from enum import Enum


class TestGuardedEnum:
    """Tests for GuardedEnum type."""
    
    def setup_method(self):
        """Create test enum for each test."""
        @guarded_enum
        class Status(Enum):
            PENDING = "pending"
            ACTIVE = "active"
            DONE = "done"
        
        self.Status = Status
    
    def test_enum_by_name(self):
        """Test creation by member name."""
        s = self.Status("PENDING")
        assert s.name == "PENDING"
        assert s.value == "pending"
    
    def test_enum_case_insensitive(self):
        """Test case-insensitive parsing."""
        s1 = self.Status("active")
        s2 = self.Status("ACTIVE")
        s3 = self.Status("Active")
        
        assert s1.name == "ACTIVE"
        assert s2.name == "ACTIVE"
        assert s3.name == "ACTIVE"
    
    def test_enum_by_value(self):
        """Test creation by member value."""
        s = self.Status("pending")
        assert s.name == "PENDING"
        assert s.value == "pending"
    
    def test_enum_repr(self):
        """Test string representation."""
        s = self.Status("active")
        assert repr(s) == "<Status.ACTIVE: 'active'>"
    
    def test_enum_equality(self):
        """Test equality comparison."""
        s1 = self.Status("active")
        s2 = self.Status("ACTIVE")
        s3 = self.Status("done")
        
        assert s1 == s2
        assert s1 != s3
    
    # def test_enum_equality_with_string(self):
    #     """Test equality with string."""
    #     s = self.Status("active")
    #     assert s == "ACTIVE"
    
    def test_enum_metadata(self):
        """Test that enum has metadata."""
        s = self.Status("active")
        assert hasattr(s, 'uncertainty')
        assert hasattr(s, 'abstraction_level')
        assert s.uncertainty <= Tolerance.PRECISE
    
    # def test_enum_unwrap(self):
    #     """Test unwrap method."""
    #     s = self.Status("active")
    #     assert s.unwrap() == "ACTIVE"
    
    def test_invalid_enum_value(self):
        """Test that invalid value raises error."""
        with pytest.raises(ValueError):
            self.Status("invalid")
    
    def test_enum_members(self):
        """Test that enum has correct members."""
        assert "PENDING" in self.Status._members
        assert "ACTIVE" in self.Status._members
        assert "DONE" in self.Status._members
        assert len(self.Status._members) == 3


class TestGuardedEnumAdvanced:
    """Advanced tests for GuardedEnum."""
    
    def test_numeric_enum(self):
        """Test enum with numeric values."""
        
        @guarded_enum
        class Priority(Enum):
            LOW = 1
            MEDIUM = 2
            HIGH = 3
        
        p = Priority(2)
        assert p.name == "MEDIUM"
        assert p.value == 2
    
    def test_mixed_value_types(self):
        """Test enum with mixed value types."""
        @guarded_enum
        class Mixed(Enum):
            STRING = "text"
            NUMBER = 42
            FLOAT = 3.14
        
        m1 = Mixed("text")
        assert m1.name == "STRING"
        
        m2 = Mixed(42)
        assert m2.name == "NUMBER"
    
    def test_enum_inheritance(self):
        """Test that enum can be subclassed."""
        @guarded_enum
        class BaseStatus(Enum):
            PENDING = "pending"
            DONE = "done"
        
        # Should work
        s = BaseStatus("pending")
        assert s.name == "PENDING"
    
    def test_enum_json_schema(self):
        """Test that enum has correct JSON schema."""
        @guarded_enum
        class Color(Enum):
            RED = "red"
            GREEN = "green"
            BLUE = "blue"
        
        assert Color._type_json["type"] == "string"
        assert set(Color._type_json["enum"]) == {"RED", "GREEN", "BLUE"}
    
    def test_enum_type_description(self):
        """Test that enum has correct type description."""
        @guarded_enum
        class Status(Enum):
            ACTIVE = "active"
        
        assert "Status" in Status._type_en
        assert "enum" in Status._type_en.lower()


class TestGuardedEnumEdgeCases:
    """Test edge cases for GuardedEnum."""
    
    def test_empty_enum(self):
        """Test enum with no members."""
        @guarded_enum
        class Empty(Enum):
            pass
        
        assert len(Empty._members) == 0
    
    def test_single_member_enum(self):
        """Test enum with single member."""
        @guarded_enum
        class Single(Enum):
            ONLY = "only"
        
        s = Single("only")
        assert s.name == "ONLY"
    
    def test_enum_with_special_names(self):
        """Test enum with names that could conflict."""
        @guarded_enum
        class Special(Enum):
            _members = "not_a_dict"  # This should be overridden
            VALUE = "value"
        
        # _members should be a dict, not the string
        assert isinstance(Special._members, dict)
        assert "VALUE" in Special._members
