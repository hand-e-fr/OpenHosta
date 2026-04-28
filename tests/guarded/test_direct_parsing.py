import pytest
from typing import List
from OpenHosta.guarded.resolver import TypeResolver
from OpenHosta.guarded import GuardedInt, Tolerance

def test_doc_example_10_1():
    """Verify example 10.1 from documentation: List parsing with prefix noise."""
    MyType = List[int]
    # This is exactly what the user tried
    raw_output = "I found these numbers: [10, 20, 30] # and some noise"
    
    guarded_type = TypeResolver.resolve(MyType)
    result = guarded_type.attempt(raw_output)
    
    assert result.success, f"Should parse list even with prefix noise. Error: {result.error_message}"
    assert result.data == [10, 20, 30]

def test_doc_example_10_3_strict():
    """Verify example 10.3 from documentation: STRICT tolerance."""
    # STRICT should reject noise
    result = GuardedInt.attempt("42 # with comments", tolerance=Tolerance.STRICT)
    assert not result.success

def test_doc_example_10_3_flexible():
    """Verify example 10.3 from documentation: FLEXIBLE tolerance."""
    # FLEXIBLE should accept comments
    result = GuardedInt.attempt("42 # with comments", tolerance=Tolerance.FLEXIBLE)
    assert result.success
    assert result.data == 42

def test_prefix_noise_scalar():
    """Verify scalar parsing with prefix noise."""
    result = GuardedInt.attempt("The age is: 42", tolerance=Tolerance.FLEXIBLE)
    assert result.success
    assert result.data == 42

def test_prefix_noise_complex():
    """Verify complex parsing with prefix noise."""
    from OpenHosta.guarded import GuardedComplex
    result = GuardedComplex.attempt("Result: 1+2j", tolerance=Tolerance.FLEXIBLE)
    assert result.success
    assert result.data == 1+2j

def test_prefix_noise_optional():
    """Verify optional parsing with prefix noise."""
    from typing import Optional
    guarded_type = TypeResolver.resolve(Optional[int])
    result = guarded_type.attempt("The value is: 42", tolerance=Tolerance.FLEXIBLE)
    assert result.success
    assert result.data == 42
    
    result_none = guarded_type.attempt("The value is: None", tolerance=Tolerance.FLEXIBLE)
    assert result_none.success
    assert result_none.data is None

def test_prefix_noise_dict():
    """Verify dict parsing with prefix noise."""
    from typing import Dict
    guarded_type = TypeResolver.resolve(Dict[str, int])
    result = guarded_type.attempt("Here is the dict: {'a': 1, 'b': 2}", tolerance=Tolerance.FLEXIBLE)
    assert result.success
    assert result.data == {'a': 1, 'b': 2}

def test_prefix_noise_dataclass():
    """Verify dataclass parsing with prefix noise."""
    from OpenHosta.guarded import guarded_dataclass
    
    @guarded_dataclass
    class Person:
        name: str
        age: int
        
    guarded_type = TypeResolver.resolve(Person)
    result = guarded_type.attempt("Created person: Person(name='Bob', age=30)", tolerance=Tolerance.FLEXIBLE)
    assert result.success
    assert result.data.name == "Bob"
    assert result.data.age == 30

def test_prefix_noise_pydantic():
    """Verify pydantic parsing with prefix noise."""
    from pydantic import BaseModel
    class User(BaseModel):
        id: int
        username: str
        
    guarded_type = TypeResolver.resolve(User)
    result = guarded_type.attempt("User data: {'id': 123, 'username': 'alice'}", tolerance=Tolerance.FLEXIBLE)
    assert result.success
    assert result.data.id == 123
    assert result.data.username == 'alice'

def test_prefix_noise_literal():
    """Verify literal parsing with prefix noise."""
    from typing import Literal
    guarded_type = TypeResolver.resolve(Literal["A", "B"])
    result = guarded_type.attempt("Option chosen: 'A'", tolerance=Tolerance.FLEXIBLE)
    assert result.success
    assert result.data == "A"
