import pytest
import time as t
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from OpenHosta import *

config.set_default_apiKey("")

def emulate_1arg_str(arg)->str:
    """ Docstring """
    return emulate()

def emulate_1arg_int(arg)->int:
    """ Docstring """
    return emulate()

def emulate_1arg_float(arg)->float:
    """ Docstring """
    return emulate()

def emulate_1arg_list(arg)->list:
    """ Docstring """
    return emulate()

def emulate_1arg_pydantic(arg)->str:
    """ Docstring """
    return emulate()

emulate_1arg = {"str": emulate_1arg_str, "int": emulate_1arg_int, "float": emulate_1arg_float, "list": emulate_1arg_list, "pydantic": emulate_1arg_pydantic}

class TestEmulate:
        
    @pytest.mark.parametrize("type, name, doc, arg, expected", [
        ("str", "generator", "generates a sentence", "", str),
        ("int", "generator", "generates an integer", "", int),
        ("list", "generator", "generates a list in python", "", list),
        ("float", "generator", "generates a float in python", "", float),
    ])
    def test_basicType(self, type, name, doc, arg, expected):
        global emulate_1arg
        emulate_1arg[type].__name__ = name
        emulate_1arg[type].__doc__ = doc
        result = emulate_1arg[type](arg)
        print(f"[{doc}]: {result}")
        assert isinstance(result, expected)
    
    @pytest.mark.parametrize("type, name, doc, arg, expected", [
        ("str", "generator", "generates a sentence", "", str),
        ("int", "generator", "generates an integer", "", int),
        ("list", "generator", "generates a list in python", "", list),
        ("float", "generator", "generates a float in python", "", float),
    ])
    def test_basicSpecial(self, type, name, doc, arg, expected):
        global emulate_1arg
        emulate_1arg[type].__name__ = name
        emulate_1arg[type].__doc__ = doc
        result = emulate_1arg[type](arg)
        print(f"[{doc}]: {result}")
        assert isinstance(result, expected)
    
    
    
class test_pydantic:
    pass

class test_suggest:
    pass

class test_thought:
    pass

class test_config:
    pass

def power(a):
    return emulate()

print(power(2))