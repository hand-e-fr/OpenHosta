import pytest
from enum import Enum
from pydantic import BaseModel
from OpenHosta.guarded import (
    GuardedInt, GuardedUtf8, 
    GuardedList, GuardedDict, GuardedTuple,
    TypeResolver, GuardedEnum
)

def test_scalar_consistency():
    """Test consistency for scalar types."""
    res = GuardedInt.attempt("42")
    assert res.success
    assert res.data == 42
    assert isinstance(res.guarded_data, GuardedInt)
    assert res.guarded_data.unwrap() == res.data
    
    res_str = GuardedUtf8.attempt(b"hello")
    assert res_str.success
    assert res_str.data == "hello"
    assert type(res_str.data) is str
    assert res_str.guarded_data.unwrap() == res_str.data

def test_list_consistency():
    """Test consistency for GuardedList[GuardedInt]."""
    IntList = GuardedList[GuardedInt]
    res = IntList.attempt(["1", 2, " 3 "])
    assert res.success
    assert res.data == [1, 2, 3]
    assert all(type(x) is int for x in res.data)
    assert isinstance(res.guarded_data, GuardedList)
    assert res.guarded_data.unwrap() == res.data

def test_tuple_consistency():
    """Test consistency for GuardedTuple[GuardedInt, GuardedUtf8]."""
    MyTuple = GuardedTuple[GuardedInt, GuardedUtf8]
    res = MyTuple.attempt(("42", b"world"))
    assert res.success
    assert res.data == (42, "world")
    assert type(res.data[0]) is int
    assert type(res.data[1]) is str
    assert res.guarded_data.unwrap() == res.data

def test_dict_consistency():
    """Test consistency for GuardedDict[GuardedUtf8, GuardedInt]."""
    MyDict = GuardedDict[GuardedUtf8, GuardedInt]
    res = MyDict.attempt({"a": "1", "b": 2})
    assert res.success
    assert res.data == {"a": 1, "b": 2}
    assert type(res.data["a"]) is int
    assert res.guarded_data.unwrap() == res.data

def test_enum_consistency():
    """Test consistency for GuardedEnum."""
    class Color(Enum):
        RED = "red"
        BLUE = "blue"
    
    from OpenHosta.guarded.subclassableclasses import guarded_enum
    GColor = guarded_enum(Color)
    
    res = GColor.attempt("RED")
    assert res.success
    assert res.data == Color.RED
    assert res.guarded_data.unwrap() == res.data

def test_pydantic_consistency():
    """Test consistency for GuardedPydanticModel (recursive)."""
    class User(BaseModel):
        id: int
        name: str

    GuardedUser = TypeResolver.resolve(User)
    
    res = GuardedUser.attempt('User(id="123", name=b"Alice")')
    assert res.success
    assert isinstance(res.data, User)
    assert res.data.id == 123
    assert res.data.name == "Alice"
    # Internal types should be native in res.data
    assert type(res.data.id) is int
    assert type(res.data.name) is str
    
    assert res.guarded_data.unwrap() == res.data
    
def test_nested_pydantic_consistency():
    """Test deep recursive Pydantic structures."""
    class Item(BaseModel):
        name: str
    
    class Box(BaseModel):
        items: list[Item]
        
    GuardedBox = TypeResolver.resolve(Box)
    
    input_val = {"items": [{"name": "item1"}, {"name": b"item2"}]}
    res = GuardedBox.attempt(input_val)
    assert res.success
    assert isinstance(res.data, Box)
    assert len(res.data.items) == 2
    assert all(isinstance(x, Item) for x in res.data.items)
    
    # Check that it's fully native strings inside
    assert type(res.data.items[1].name) is str
    assert res.data.items[1].name == "item2"
    
    assert res.guarded_data.unwrap() == res.data
