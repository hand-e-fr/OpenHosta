import pytest
from pydantic import BaseModel
import re
from typing import (
    Any,
    Dict,
    get_args,
    get_origin,
    Union,
    List,
    Tuple,
    Mapping,
    Sequence,
    Collection,
    Literal,
    Final,
    Type,
    Annotated,
    ClassVar,
    Protocol,
    AnyStr,
    ByteString,
    Set,
    FrozenSet,
    AbstractSet,
    Optional,
    Callable,
    OrderedDict,
    TypeVar,
    NamedTuple,
    TypedDict
)

from OpenHosta import emulate

class TestTypes:
    
    def test_NativeNumericalInt(self):
        def add_two(a:int)->int:
            """
            This function adds two to the integers in parameter
            """
            return emulate()
        
        assert type(add_two(2)) == int
        
    def test_NativeNumericalFloat(self):
        def add_zeropointtwo(a:float)->float:
            """
            This function adds 0.2 to the float in parameter
            """
            return emulate()
        
        assert type(add_zeropointtwo(2.2)) == float
        
    def test_NativeNumericalComplex(self):
        def complex_func(a:complex)->complex:
            """
            This function will bug anyway so don't bother me
            """
            return emulate()
        
        with pytest.raises(ValueError, match=re.escape(f"<class 'complex'> type is not supported please check here to see the supported types : https://github.com/hand-e-fr/OpenHosta/blob/dev/docs/doc.md#:~:text=bool.%20The-,complex,-type%20is%20not")):
            complex_func(complex(1))
        
    def test_NativeNumericalBool(self):
        def inverse_bool(a:bool)->bool:
            """
            This function return True if a is False and False if a is True.
            """
            return emulate()
        
        assert type(inverse_bool(True)) == bool
        
    def test_NativeSequentialStr(self):
        def return_str(a:str)->str:
            """
            This function returns a string in parameter.
            """
            return emulate()
        
        assert type(return_str("hi mom")) == str

    def test_NativeSequentialList(self):
        def random_list(a:list)->list:
            """
            This function return a list of random number of the length of the list in parameter.
            """
            return emulate()
        
        assert type(random_list([1, 2, 3])) == list
    
    def test_NativeSequentialTuple(self):
        def random_tuple(a:tuple)->tuple:
            """
            This function returns a tuple containing the same elements as the tuple in parameter.
            """
            return emulate()
        
        assert type(random_tuple((5, "aaaaaaah"))) == tuple

    
    def test_NativeSequentialRange(self):
        def range_func(a:range)->range:
            """
            This function will bug anyway so don't bother me
            """
            return emulate()
        
        with pytest.raises(ValueError, match=re.escape(f"<class 'range'> type is not supported please check here to see the supported types : https://github.com/hand-e-fr/OpenHosta/blob/dev/docs/doc.md#:~:text=bool.%20The-,complex,-type%20is%20not")):
            range_func(range(1))
            
    def test_NativeMappinDict(self):
        def count_dict(a:dict)->dict:
            """
            This function returns a dict containing as a key the name of the dict in paramter and as a value his length
            """
            return emulate()
        
        assert type(count_dict({"tata": 4, "titi": 2})) == dict
        
    def test_NativeEnsembleSet(self):
        def return_set(a:set)->set:
            """
            This function returns the same set as the parameter
            """
            return emulate()
        
        msg=""
        try:
            return_set([1, 2, 3])
        except ValueError as e:
            msg = str(e)
        assert "type is not supported" in msg

        
    def test_NativeEnsembleFrozenset(self):
        def return_frozenset(a:frozenset)->frozenset:
            """
            This function returns the same frozenset as the parameter
            """
            return emulate()
        
        assert type(return_frozenset(frozenset([1, 2, 3, 4]))) == frozenset
        
    def test_NativeBinaryBytes(self):
        def return_byte(a:bytes)->bytes:
            """
            This function return the same bytes as the parameter
            """
            return emulate()
        
        assert type(return_byte(bytes("hi mom", encoding='utf-8'))) == bytes
        
    def test_NativeBinaryBytearray(self):
        def return_byte(a:bytearray)->bytearray:
            """
            This function return the same bytearray as the parameter
            """
            return emulate()
        
        assert type(return_byte(bytearray("hi mom", encoding='utf-8'))) == str
        
    def test_NativeNone(self):
        def return_none():
            """
            This function returns None
            """   
            return emulate()
        
        assert return_none() is None
        
    def test_TypingList(self):
        def return_int_list(a: List[int]) -> List[int]:
            """
            This function returns a list of integers
            """
            return emulate()
        
        assert type(return_int_list([1, 2, 3])) == list

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
        def return_optional(a: Optional[int]) -> Optional[int]:
            """
            This function returns either an integer or None
            """
            return emulate()
        
        assert type(return_optional(1)) in (int, type(None))

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
        
        msg=""
        try:
            return_sequence([1, 2, 3])
        except ValueError as e:
            msg = str(e)
        assert "type is not supported" in msg

    def test_TypingMapping(self):
        def return_mapping(a: Mapping[str, int]) -> Mapping[str, int]:
            """
            This function returns a mapping of strings to integers
            """
            return emulate()
        
        msg=""
        try:
            return_mapping({"test": 1})
        except ValueError as e:
            msg = str(e)
        assert "type is not supported" in msg

    def test_TypingNamedTuple(self):
        class TestNamedTuple(NamedTuple):
            name: str
            age: int
        
        def return_named_tuple(a: TestNamedTuple) -> TestNamedTuple:
            """
            This function returns a named tuple
            """
            return emulate()
        
        with pytest.raises(ValueError):
            return_named_tuple(TestNamedTuple("John", 30))

    def test_TypingTypedDict(self):
        class TestTypedDict(TypedDict):
            name: str
            age: int
        
        def return_typed_dict(a: TestTypedDict) -> TestTypedDict:
            """
            This function returns a typed dict
            """
            return emulate()
        
        assert type(return_typed_dict({"name": "John", "age": 30})) == dict

    def test_TypingAny(self):
        def return_any(a: Any) -> Any:
            """
            This function returns any type
            """
            return emulate()
        
        assert return_any(1) is not None