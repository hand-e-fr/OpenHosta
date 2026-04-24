import pytest
from typing import List, Dict, Set, Tuple, Optional, Union, Literal
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel
from OpenHosta.guarded.resolver import TypeResolver

@dataclass
class Person:
    name: str
    age: int

class Color(Enum):
    RED = "red"
    GREEN = "green"

class Item(BaseModel):
    id: int
    name: str

def format_scenario(scenario: str, value: str) -> str:
    if scenario == "direct_oneline":
        return value
    if scenario == "direct_multiline":
        return f"\n{value}\n"
    if scenario == "python_block_comments":
        return f"```python\n# Result follows\n{value} # The actual result\n```"
    if scenario == "answer_blank_explanation":
        return f"{value}\n\nThis is the explanation of why the result is what it is."
    if scenario == "python_block_surrounding":
        return f"Here is the result you asked for:\n```python\n{value}\n```\nHope this helps!"
    if scenario == "multiline_structured_comments":
        # Simulate multiline with comments on each line
        lines = value.split("\n")
        return "\n".join(f"{line} # comment" for line in lines)
    if scenario == "broken_python_star_comments":
        # Simulate non-standard comments and extra text at the end
        return f"{value} * this is a non-standard comment\n* end of page comment"
    return value

SCENARIOS = [
    "direct_oneline",
    "direct_multiline",
    "python_block_comments",
    "answer_blank_explanation",
    "python_block_surrounding",
    "multiline_structured_comments",
    "broken_python_star_comments",
]

class TestScalarBorderlines:
    
    @pytest.mark.parametrize("scenario", SCENARIOS)
    def test_int(self, scenario):
        guarded_type = TypeResolver.resolve(int)
        raw = format_scenario(scenario, "42")
        result = guarded_type.attempt(raw)
        assert result.success, f"Failed for scenario {scenario}: {result.error_message}"
        assert result.data == 42

    @pytest.mark.parametrize("scenario", SCENARIOS)
    def test_float(self, scenario):
        guarded_type = TypeResolver.resolve(float)
        raw = format_scenario(scenario, "3.14")
        result = guarded_type.attempt(raw)
        assert result.success, f"Failed for scenario {scenario}: {result.error_message}"
        assert abs(result.data - 3.14) < 1e-6

    @pytest.mark.parametrize("scenario", SCENARIOS)
    def test_bool(self, scenario):
        guarded_type = TypeResolver.resolve(bool)
        raw = format_scenario(scenario, "True")
        result = guarded_type.attempt(raw)
        assert result.success, f"Failed for scenario {scenario}: {result.error_message}"
        assert result.data is True

    @pytest.mark.parametrize("scenario", SCENARIOS)
    def test_complex(self, scenario):
        guarded_type = TypeResolver.resolve(complex)
        raw = format_scenario(scenario, "1+2j")
        result = guarded_type.attempt(raw)
        assert result.success, f"Failed for scenario {scenario}: {result.error_message}"
        assert result.data == 1+2j

class TestCollectionBorderlines:
    
    @pytest.mark.parametrize("scenario", SCENARIOS)
    def test_list_int(self, scenario):
        guarded_type = TypeResolver.resolve(List[int])
        raw = format_scenario(scenario, "[1, 2, 3]")
        result = guarded_type.attempt(raw)
        assert result.success, f"Failed for scenario {scenario}: {result.error_message}"
        assert result.data == [1, 2, 3]

    @pytest.mark.parametrize("scenario", SCENARIOS)
    def test_dict_str_int(self, scenario):
        guarded_type = TypeResolver.resolve(Dict[str, int])
        raw = format_scenario(scenario, '{"a": 1, "b": 2}')
        result = guarded_type.attempt(raw)
        assert result.success, f"Failed for scenario {scenario}: {result.error_message}"
        assert result.data == {"a": 1, "b": 2}

    @pytest.mark.parametrize("scenario", SCENARIOS)
    def test_set_str(self, scenario):
        guarded_type = TypeResolver.resolve(Set[str])
        raw = format_scenario(scenario, "{'a', 'b'}")
        result = guarded_type.attempt(raw)
        assert result.success, f"Failed for scenario {scenario}: {result.error_message}"
        assert result.data == {"a", "b"}

    @pytest.mark.parametrize("scenario", SCENARIOS)
    def test_tuple_int_str(self, scenario):
        guarded_type = TypeResolver.resolve(Tuple[int, str])
        raw = format_scenario(scenario, "(1, 'a')")
        result = guarded_type.attempt(raw)
        assert result.success, f"Failed for scenario {scenario}: {result.error_message}"
        assert result.data == (1, 'a')

class TestStructuredBorderlines:
    
    @pytest.mark.parametrize("scenario", SCENARIOS)
    def test_dataclass(self, scenario):
        guarded_type = TypeResolver.resolve(Person)
        raw_val = "Person(name='George', age=67)"
        raw = format_scenario(scenario, raw_val)
        result = guarded_type.attempt(raw)
        assert result.success, f"Failed for scenario {scenario}: {result.error_message}"
        assert result.data.name == "George"
        assert result.data.age == 67

    @pytest.mark.parametrize("scenario", SCENARIOS)
    def test_pydantic(self, scenario):
        guarded_type = TypeResolver.resolve(Item)
        raw_val = "Item(id=1, name='Laptop')"
        raw = format_scenario(scenario, raw_val)
        result = guarded_type.attempt(raw)
        assert result.success, f"Failed for scenario {scenario}: {result.error_message}"
        assert result.data.id == 1
        assert result.data.name == "Laptop"

class TestAdvancedBorderlines:

    @pytest.mark.parametrize("scenario", SCENARIOS)
    def test_optional_int(self, scenario):
        guarded_type = TypeResolver.resolve(Optional[int])
        # Test with value
        raw = format_scenario(scenario, "42")
        result = guarded_type.attempt(raw)
        assert result.success, f"Failed for scenario {scenario} (value): {result.error_message}"
        assert result.data == 42
        
        # Test with None
        raw_none = format_scenario(scenario, "None")
        result_none = guarded_type.attempt(raw_none)
        assert result_none.success, f"Failed for scenario {scenario} (None): {result_none.error_message}"
        assert result_none.data is None

    @pytest.mark.parametrize("scenario", SCENARIOS)
    def test_union_int_str(self, scenario):
        guarded_type = TypeResolver.resolve(Union[int, str])
        # Should favor int if possible
        raw = format_scenario(scenario, "42")
        result = guarded_type.attempt(raw)
        assert result.success, f"Failed for scenario {scenario} (int): {result.error_message}"
        assert result.data == 42

        # Fallback to str
        raw_str = format_scenario(scenario, "'hello'")
        result_str = guarded_type.attempt(raw_str)
        assert result_str.success, f"Failed for scenario {scenario} (str): {result_str.error_message}"
        assert result_str.data == "hello"

    @pytest.mark.parametrize("scenario", SCENARIOS)
    def test_literal(self, scenario):
        guarded_type = TypeResolver.resolve(Literal["A", "B"])
        raw = format_scenario(scenario, "'A'")
        result = guarded_type.attempt(raw)
        assert result.success, f"Failed for scenario {scenario}: {result.error_message}"
        assert result.data == "A"

    @pytest.mark.parametrize("scenario", SCENARIOS)
    def test_enum(self, scenario):
        guarded_type = TypeResolver.resolve(Color)
        raw = format_scenario(scenario, "Color.RED")
        result = guarded_type.attempt(raw)
        assert result.success, f"Failed for scenario {scenario}: {result.error_message}"
        assert result.data == Color.RED
