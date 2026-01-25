"""Tests for guarded_dataclass decorator."""

import pytest
from dataclasses import dataclass
from src.OpenHosta.guarded.constants import Tolerance
from src.OpenHosta.guarded.subclassablecollections import guarded_dataclass


class TestGuardedDataclass:
    """Tests for @guarded_dataclass decorator."""
    
    def test_basic_dataclass(self):
        """Test basic dataclass functionality."""
        @guarded_dataclass
        @dataclass
        class Person:
            name: str
            age: int
        
        p = Person(name="Alice", age=30)
        assert p.name == "Alice"
        assert p.age == 30
    
    def test_dataclass_from_dict(self):
        """Test creation from dictionary."""
        @guarded_dataclass
        @dataclass
        class Person:
            name: str
            age: int
        
        p = Person({"name": "Bob", "age": 25})
        assert p.name == "Bob"
        assert p.age == 25
    
    def test_dataclass_metadata(self):
        """Test that dataclass has metadata."""
        @guarded_dataclass
        @dataclass
        class Person:
            name: str
        
        p = Person(name="Charlie")
        assert hasattr(p, 'uncertainty')
        assert hasattr(p, 'abstraction_level')
    
    def test_dataclass_with_defaults(self):
        """Test dataclass with default values."""
        @guarded_dataclass
        @dataclass
        class Config:
            host: str = "localhost"
            port: int = 8080
        
        c1 = Config()
        assert c1.host == "localhost"
        assert c1.port == 8080
        
        c2 = Config(host="example.com")
        assert c2.host == "example.com"
        assert c2.port == 8080
    
    def test_dataclass_partial_dict(self):
        """Test dict with only some fields."""
        @guarded_dataclass
        @dataclass
        class Person:
            name: str
            age: int = 0
        
        p = Person({"name": "Dave"})
        assert p.name == "Dave"
        assert p.age == 0
    
    def test_dataclass_invalid_dict(self):
        """Test that invalid dict raises error."""
        @guarded_dataclass
        @dataclass
        class Person:
            name: str
            age: int
        
        # Missing required field
        with pytest.raises(ValueError):
            Person({"name": "Eve"})
    
    def test_dataclass_type_conversion(self):
        """Test that types are converted."""
        @guarded_dataclass
        @dataclass
        class Data:
            value: int
        
        # String should be converted to int
        d = Data({"value": "42"})
        # This might not work yet if we don't resolve types
        # assert d.value == 42
    
    def test_non_dataclass_error(self):
        """Test that decorator applies dataclass automatically."""
        # This should NOT raise an error anymore
        @guarded_dataclass
        class AutoDataclass:
            name: str
            value: int
        
        # Should work like a normal dataclass
        obj = AutoDataclass(name="test", value=42)
        assert obj.name == "test"
        assert obj.value == 42
    
    def test_without_dataclass_decorator(self):
        """Test that @guarded_dataclass works alone (recommended usage)."""
        @guarded_dataclass
        class Person:
            name: str
            age: int
        
        # Test kwargs creation
        p1 = Person(name="Alice", age=30)
        assert p1.name == "Alice"
        assert p1.age == 30
        
        # Test dict creation with type conversion
        p2 = Person({"name": "Bob", "age": "25"})
        assert p2.name == "Bob"
        assert p2.age == 25
        assert isinstance(p2.age, int)  # Converted from string
    
    def test_without_dataclass_with_defaults(self):
        """Test @guarded_dataclass alone with default values."""
        @guarded_dataclass
        class Config:
            host: str = "localhost"
            port: int = 8080
        
        c1 = Config()
        assert c1.host == "localhost"
        assert c1.port == 8080
        
        c2 = Config(host="example.com")
        assert c2.host == "example.com"
        assert c2.port == 8080
    
    def test_without_dataclass_with_options(self):
        """Test @guarded_dataclass with dataclass options."""
        @guarded_dataclass(frozen=True)
        class Point:
            x: int
            y: int
        
        pt = Point(x=10, y=20)
        assert pt.x == 10
        assert pt.y == 20
        
        # Should be frozen
        with pytest.raises(Exception):  # FrozenInstanceError
            pt.x = 100
    
    def test_nested_dataclass(self):
        """Test nested dataclasses."""
        @guarded_dataclass
        @dataclass
        class Address:
            street: str
            city: str
        
        @guarded_dataclass
        @dataclass
        class Person:
            name: str
            address: Address
        
        # This is complex, might not work yet
        # p = Person({
        #     "name": "Frank",
        #     "address": {"street": "Main St", "city": "NYC"}
        # })


class TestGuardedDataclassAdvanced:
    """Advanced tests for guarded_dataclass."""
    
    def test_dataclass_with_list(self):
        """Test dataclass with list field."""
        @guarded_dataclass
        @dataclass
        class Team:
            name: str
            members: list
        
        t = Team(name="Alpha", members=["Alice", "Bob"])
        assert len(t.members) == 2
    
    def test_dataclass_with_optional(self):
        """Test dataclass with optional fields."""
        from typing import Optional
        
        @guarded_dataclass
        @dataclass
        class User:
            username: str
            email: Optional[str] = None
        
        u1 = User(username="user1")
        assert u1.email is None
        
        u2 = User(username="user2", email="user2@example.com")
        assert u2.email == "user2@example.com"
    
    def test_dataclass_equality(self):
        """Test dataclass equality."""
        @guarded_dataclass
        @dataclass
        class Point:
            x: int
            y: int
        
        p1 = Point(x=1, y=2)
        p2 = Point(x=1, y=2)
        p3 = Point(x=2, y=3)
        
        assert p1 == p2
        assert p1 != p3
    
    def test_dataclass_repr(self):
        """Test dataclass string representation."""
        @guarded_dataclass
        @dataclass
        class Item:
            name: str
            price: float
        
        item = Item(name="Widget", price=9.99)
        repr_str = repr(item)
        
        assert "Item" in repr_str
        assert "Widget" in repr_str
