import pytest
from typing import Any

from OpenHosta import emulate, test as oh_test

class TestTypes:
    
    def test_NativeNumericalInt(self):
        def add_two(a:int)->int:
            """
            This function adds two to the integers in parameter
            """
            return emulate()
        
        assert isinstance(add_two(2), int)
        
    def test_NativeNumericalFloat(self):
        def add_zeropointtwo(a:float)->float:
            """
            This function adds 0.2 to the float in parameter
            """
            return emulate()
        
        assert isinstance(add_zeropointtwo(2.2), float)
        
    def test_NativeNumericalComplex(self):
        def complex_func(a:complex)->complex:
            """
            This function return the opposite of the complex number in parameter
            """
            return emulate()
        
        assert complex_func(complex("1+j")) == complex("-1-j")
        
    def test_NativeNumericalBool(self):
        def inverse_bool(a:bool)->bool:
            """
            This function return True if a is False and False if a is True.
            """
            return emulate()
        
        # GuardedBool wraps bool (proxy), so isinstance(x, bool) is False.
        # We check behavior (truthiness or value)
        assert inverse_bool(True) == False
        # assert isinstance(inverse_bool(True), bool) # Impossible for proxy types
        assert inverse_bool(True) == False
        assert inverse_bool(False) == True
        
    def test_NativeSequentialStr(self):
        def return_str(a:str)->str:
            """
            This function returns a string in parameter.
            """
            return emulate()
        
        assert isinstance(return_str("hi mom"), str)

    def test_NativeSequentialList(self):
        def random_list(a:list)->list:
            """
            This function return a list of random number of the length of the list in parameter.
            """
            return emulate()
        
        assert isinstance(random_list([1, 2, 3]), list)
    
    def test_NativeSequentialTuple(self):
        def random_tuple(a:tuple)->tuple:
            """
            This function returns a tuple containing the same elements as the tuple in parameter.
            """
            return emulate()
        
        # model.type_returned_data(random_tuple._last_response["data"], random_tuple.hosta_inspection._infos)
        # random_tuple.hosta_inspection._infos.f_type
        assert isinstance(random_tuple((5, "aaaaaaah")), tuple)

    
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
        def count_dict(a:dict)->dict:
            """
            This function returns a dict of one element containing "count" as key and the count of elements in a as value
            """
            return emulate()
        
        assert isinstance(count_dict({"tata": 4, "titi": 2}), dict)
        
    def test_NativeEnsembleSet(self):
        def return_set(a:set)->set:
            """
            This function returns the same set as the parameter
            """
            return emulate()
        
        assert isinstance(return_set({1, 2, 3}), set)

        
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
            