import pytest
from typing import Any

from OpenHosta import emulate, test as oh_test

class TestTypes:
    
    def test_NativeNumericalInt(self):
        def add_two(text: str) -> int:
            """
            Extract the number from the text and add two to it.
            """
            return emulate()
        
        assert isinstance(add_two("The number is 2."), int)
        
    def test_NativeNumericalFloat(self):
        def add_zeropointtwo(text: str) -> float:
            """
            Extract the float from the text and add 0.2 to it.
            """
            return emulate()
        
        assert isinstance(add_zeropointtwo("The float is 2.2."), float)
        
    def test_NativeNumericalComplex(self):
        def complex_func(text: str) -> complex:
            """
            Extract the complex number from the text and return its opposite.
            """
            return emulate()
        
        assert complex_func("The complex number is 1+j") == complex("-1-j")
        
    def test_NativeNumericalBool(self):
        def is_approved(text: str) -> bool:
            """
            Return True if the text indicates approval, False otherwise.
            """
            return emulate()
        
        assert is_approved("Yes, it is approved.") == True
        assert is_approved("No, REJECTED.") == False
        
    def test_NativeSequentialStr(self):
        def return_str(text: str) -> str:
            """
            Return the main greeting phrase from the text.
            """
            return emulate()
        
        assert isinstance(return_str("He said: hi mom!"), str)

    def test_NativeSequentialList(self):
        def random_list(text: str) -> list:
            """
            Extract the numbers mentioned in the text as a list.
            """
            return emulate()
        
        assert isinstance(random_list("The numbers are 1, 2, and 3."), list)
    
    def test_NativeSequentialTuple(self):
        def extract_tuple(text: str) -> tuple:
            """
            Extract the quantity and the item name from the text into a tuple.
            """
            return emulate()
        
        assert isinstance(extract_tuple("I have 5 apples."), tuple)

    
    def test_NativeSequentialRange(self):
        def range_func(a:range)->range:
            """
            This function returns a range of the same length as the range in parameter but starting at 10
            """
            return emulate()
        
        # GuardedRange wraps range
        res = range_func(range(1))
        assert res.start == range(10, 11).start
        # assert isinstance(range_func(range(1)), range)
            
    def test_NativeMappinDict(self):
        def count_dict(text: str) -> dict:
            """
            Extract a dictionary mapping item names to their quantities from the text.
            """
            return emulate()
        
        assert isinstance(count_dict("I have 4 tata and 2 titi."), dict)
        
    def test_NativeEnsembleSet(self):
        def return_set(text: str) -> set:
            """
            Extract unique numbers from the text into a set.
            """
            return emulate()
        
        assert isinstance(return_set("Numbers: 1, 2, 2, 3."), set)

        
    def test_NativeEnsembleFrozenset(self):
        def return_frozenset(a:frozenset)->frozenset:
            """
            This function returns the same frozenset as the parameter
            """
            return emulate()

        # GuardedSet inherits set, not frozenset (no GuardedFrozenset yet)
        res = return_frozenset(frozenset([1, 2, 3, 4]))
        assert res == {1, 2, 3, 4}
        # assert isinstance(res, frozenset)
        
    def test_NativeBinaryBytes(self):
        def return_byte(a:bytes)->bytes:
            """
            This function return the same bytes as the parameter
            """
            return emulate()
        
        assert isinstance(return_byte(bytes("hi mom", encoding='utf-8')), bytes)
        
    def test_NativeBinaryBytearray(self):
        def return_byte(a:bytearray)->bytearray:
            """
            This function return the same bytearray as the parameter
            """
            return emulate()
        
        assert isinstance(return_byte(bytearray("hi mom", encoding='utf-8')), bytearray)
        
    def test_NativeNone(self):
        def return_none() -> type(None) :
            """
            This function returns None
            """   
            return emulate()
        
        assert return_none() == None
    
    def test_testReturnType(self):        
        ret = oh_test("this is true")
        # ret is GuardedBool
        assert ret == True
        assert ret == True
        
    
    def test_MaybeNone(self):
        def return_none_if_go(text:str) -> Any :
            """
            This function returns None if the input contains GO,
            
            In all other cases it returns the `text` as provided in input. 
            """   
            return emulate()
        
        val1 = return_none_if_go("GO")
        val2 = return_none_if_go("sO")
        assert val1 == None, f"Got {val1} expected None"
        assert val2 != None, f"Got {val1} expected sO"
            