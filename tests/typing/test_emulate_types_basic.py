import pytest

from OpenHosta import emulate, ask, test

answer = ask("Just say: The API to the model works!")
assert "The API to the model works!" in answer

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
        
        assert type(inverse_bool(True)) == bool
        assert inverse_bool(True) is False
        assert inverse_bool(False) is True
        
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
        
        # model.type_returned_data(random_tuple._last_response["data"], random_tuple.hosta_inspection._infos)
        # random_tuple.hosta_inspection._infos.f_type
        assert type(random_tuple((5, "aaaaaaah"))) == tuple

    
    def test_NativeSequentialRange(self):
        def range_func(a:range)->range:
            """
            This function returns a range of the same length as the range in parameter but starting at 10
            """
            return emulate()
        
        assert type(range_func(range(1))) is range
            
    def test_NativeMappinDict(self):
        def count_dict(a:dict)->dict:
            """
            This function returns a dict of one element containing "count" as key and the count of elements in a as value
            """
            return emulate()
        
        assert type(count_dict({"tata": 4, "titi": 2})) == dict
        
    def test_NativeEnsembleSet(self):
        def return_set(a:set)->set:
            """
            This function returns the same set as the parameter
            """
            return emulate()
        
        assert type(return_set({1, 2, 3})) == set

        
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
        
        assert type(return_byte(bytearray("hi mom", encoding='utf-8'))) == bytearray
        
    def test_NativeNone(self):
        def return_none():
            """
            This function returns None
            """   
            return emulate()
        
        assert return_none() is None
    
    def test_testReturnType(self):        
        ret = test("this is true")
        assert type(ret) == bool
        assert ret is True