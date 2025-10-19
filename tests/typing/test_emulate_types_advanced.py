import pytest

# Import types
from typing import (
    Any,
    Dict,
    Union,
    List,
    Tuple,
    Mapping,
    Sequence,
    Collection,
    Literal,
    Final,
    Annotated,
    ClassVar,
    Protocol,
    Set,
    FrozenSet,
    AbstractSet,
    Optional,
    Callable,
    OrderedDict,
    TypeVar,
    NamedTuple,
    TypedDict,
)

# Import TypeVar bound and constraints
from typing import (
    AnyStr,
    ByteString,
)

from OpenHosta import emulate, ask

answer = ask("Just say: The API to the model works!")
assert "The API to the model works!" in answer

class TestTypes:
    
    def test_TypingAnyStr(self):
        def return_set(length: int) -> Set:
            """
            This function returns a set of strings
            """
            return emulate()
        
        assert type(return_set(2)) == set
    
        
    def test_TypingList(self):
        def return_int_list(a: List[int]) -> List[int]:
            """
            This function returns a list of integers
            """
            return emulate()
        
        response = return_int_list([1.0, 2, 3])
        assert type(response) == list
        assert type(response[0]) == int
        
        def return_float_list(a: List[int]) -> List[float]:
            """
            This function returns a list of floats
            """
            return emulate()

        response = return_float_list([1, 2, 3])
        assert type(response) == list
        assert type(response[0]) == float


    def test_TypingTuple(self):
        def return_mixed_tuple(a: Tuple[int, str]) -> Tuple[int, str]:
            """
            This function returns a tuple with an integer and a string
            """
            return emulate()

        assert type(return_mixed_tuple((1, "test"))) == tuple

    def test_TypingDict(self):
        def return_str_dict(a: Dict[str, int]) -> Dict[str, int]:
            """
            This function returns a dictionary with string keys and integer values
            """
            return emulate()
        
        assert type(return_str_dict({"test": 1})) == dict

    def test_TypingSet(self):
        def return_int_set(a: Set[int]) -> Set[int]:
            """
            This function returns a set of integers
            """
            return emulate()
        
        assert type(return_int_set({1, 2, 3})) == set

    def test_TypingOptional(self):
        def return_optional(a: Optional[str]) -> Optional[int]:
            """
            This function returns the count of letters in a if a is a king name, otherwise return no value
            """
            return emulate()
        
        assert type(return_optional("Arthur")) is int
        assert type(return_optional("go have a break")) is type(None)

    def test_TypingUnion(self):
        def return_union(a: Union[int, str]) -> Union[int, str]:
            """
            This function returns either an integer or a string
            """
            return emulate()
        
        assert type(return_union(1)) in (int, str)

    def test_TypingLiteral(self):
        def return_literal(a: Literal["red", "blue"]) -> Literal["red", "blue"]:
            """
            This function returns either 'red' or 'blue'
            """
            return emulate()
        
        result = return_literal("red")
        assert result in ("red", "blue")

    def test_TypingSequence(self):
        def return_sequence(a: Sequence[int]) -> Sequence[int]:
            """
            This function returns a sequence of integers
            """
            return emulate()

        assert type(return_sequence([1, 2, 3]) ) == list

    def test_TypingMapping(self):
        def return_mapping(a: Mapping[str, int]) -> Mapping[str, int]:
            """
            This function returns a mapping of strings to integers
            """
            return emulate()
        
        assert type(return_mapping({"test": 1})) == dict


    def test_TypingNamedTuple(self):
        class TestNamedTuple(NamedTuple):
            name: str
            age: int
        
        def return_named_tuple(a: TestNamedTuple) -> TestNamedTuple:
            """
            This function returns a named tuple
            """
            return emulate()

        result = return_named_tuple(TestNamedTuple("John", 30))
        assert type(result) == tuple or type(result) == TestNamedTuple

    def test_TypingTypedDict(self):
        class TestTypedDict(TypedDict):
            name: str
            age: int
        
        def return_typed_dict(a: TestTypedDict) -> TestTypedDict:
            """
            This function returns a typed dict
            """
            return emulate()
        
        response = return_typed_dict({"name": "John", "age": 30})
        
        assert type(response) == dict

    def test_TypingAny(self):
        def return_any(a: Any) -> Any:
            """
            This function returns any type
            """
            return emulate()
        
        assert return_any(1) is not None