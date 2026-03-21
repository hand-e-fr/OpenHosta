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
        
        assert isinstance(return_set(2), set)
    
        
    def test_TypingList(self):
        def return_int_list(text: str) -> List[int]:
            """
            Extract all integers present in the text and return them as a list.
            """
            return emulate()
        
        response = return_int_list("I have 1 apple, 2 bananas, and 3 oranges.")
        assert isinstance(response, list)
        assert isinstance(response[0], int)
        
        def return_float_list(text: str) -> List[float]:
            """
            Extract all float numbers present in the text and return them as a list.
            """
            return emulate()

        response = return_float_list("Temperatures are 1.5, 2.0, and 3.5 degrees.")
        assert isinstance(response, list)
        assert isinstance(response[0], float)


    def test_TypingTuple(self):
        def return_mixed_tuple(text: str) -> Tuple[int, str]:
            """
            Extract the age (int) and name (str) from the text.
            """
            return emulate()

        assert isinstance(return_mixed_tuple("John is 30 years old."), tuple)

    def test_TypingDict(self):
        def return_str_dict(text: str) -> Dict[str, int]:
            """
            Extract a mapping of fruit names to their quantities from the text.
            """
            return emulate()
        
        assert isinstance(return_str_dict("1 apple, 2 bananas, 3 oranges"), dict)

    def test_TypingSet(self):
        def return_int_set(text: str) -> Set[int]:
            """
            Extract unique numbers from the text.
            """
            return emulate()
        
        assert isinstance(return_int_set("Numbers are 1, 2, 2, 3."), set)

    def test_TypingOptional(self):

        def count_name_letters(text: Optional[str]) -> Optional[int]:
            """
            This function returns the count of letters the firstname present in `text`.
            If no firstname can be found, return None.

            Args:
                text(str): a string that may contain a firstname

            Return:
                (int) the count of letter is the firstname present in test 
            """
            return emulate()
        
        val1 = count_name_letters("Arthur")
        # val2 = count_name_letters("go have a break to John") # Good test for uncertainty
        val3 = count_name_letters("this is not a firstname")

        assert isinstance(val1, int), f"got {val1} but expected 6"
        
        assert val3 == None, f"Shoud be None got {val3}"

    def test_TypingUnion(self):
        def return_union(text: str) -> Union[int, str]:
            """
            Extract the shipment identifier from the text.
            Return it as int if it is purely numeric, as str otherwise.
            """
            return emulate()
        
        assert isinstance(return_union("Shipment ID is 12345"), (int, str))

    def test_TypingLiteral(self):
        def return_literal(text: str) -> Literal["red", "blue"]:
            """
            Classify the color mentioned in the text as either 'red' or 'blue'.
            """
            return emulate()
        
        result = return_literal("The sky is blue today.")
        assert result in ("red", "blue")

    def test_TypingSequence(self):
        def return_sequence(text: str) -> Sequence[int]:
            """
            Extract a sequence of numbers from the text.
            """
            return emulate()

        assert isinstance(return_sequence("1, 2, 3"), list)

    def test_TypingMapping(self):
        def return_mapping(text: str) -> Mapping[str, int]:
            """
            Extract a dictionary mapping names to ages.
            """
            return emulate()
        
        assert isinstance(return_mapping("Alice is 25, Bob is 30"), dict)


    def test_TypingNamedTuple(self):
        class TestNamedTuple(NamedTuple):
            name: str
            age: int
        
        def return_named_tuple(text: str) -> TestNamedTuple:
            """
            Extract the person's name and age from the text.
            """
            return emulate()

        result = return_named_tuple("John is 30 years old.")
        assert isinstance(result, tuple)

    def test_TypingTypedDict(self):
        class TestTypedDict(TypedDict):
            name: str
            age: int
        
        def return_typed_dict(text: str) -> TestTypedDict:
            """
            Extract the person's name and age from the text into a typed dict.
            """
            return emulate()
        
        response = return_typed_dict("John is 30 years old.")
        
        assert isinstance(response, dict)

    def test_TypingAny(self):
        def return_any(text: str) -> Any:
            """
            Extract whatever information is most relevant from the text.
            """
            return emulate()
        
        assert return_any("This is a test 123") is not None
        
        

    def test_type_alias(self):
        UserType = list[dict[str, dict[str, str]]]
        
        def parse_container_manifest_user_type(text: str) -> UserType:
            """
            Extract a list of containers. Each container is a dictionary mapping the container ID
            to another dictionary of SKU codes and their descriptions.
            """
            return emulate()
        
        
        CONTAINER_MANIFEST_TEXT = (
            "Shipment includes 2 containers. "
            "Container CONT-100: SKU-A - 'Widgets', SKU-B - 'Gadgets'. "
            "Container CONT-200: SKU-C - 'Gizmos'."
        )
        
        result = parse_container_manifest_user_type(CONTAINER_MANIFEST_TEXT)

        assert isinstance(result, list)
        if len(result) > 0:
            assert isinstance(result[0], dict)
        
        assert result == [{'CONT-100': {'SKU-A': 'Widgets', 'SKU-B': 'Gadgets'}}, {'CONT-200': {'SKU-C': 'Gizmos'}}]