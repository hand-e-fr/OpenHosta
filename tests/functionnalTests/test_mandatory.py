import pytest
import time as t
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src", "OpenHosta")))

from OpenHosta import config, emulate

g_apiKey = ""

config.set_default_apiKey(g_apiKey)

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

emulate_1arg = {"str": emulate_1arg_str, "int": emulate_1arg_int, "float": emulate_1arg_float, "list": emulate_1arg_list}

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
        my_func = emulate_1arg[type]
        result = my_func(arg)
        print(f"[{doc}]: {result}")
        assert isinstance(result, expected)


    def test_FeaturesEmptyInfos(self):
        def a():
            return emulate()
        res = a()
        assert res is None
        
    def test_FeatureDecorator(self):
        
        def decorator(func):
            def wrapper(*args, **kwargs):
                res = func(*args, **kwargs)
                return res
            return wrapper
        
        @decorator
        def returntNone():
            """ This function returns None """
            return emulate()
        
        ret = returntNone()
        assert ret is None
        
    def test_FeatureClassMethod(self):
        
        class EmulateClass:
            
            def returntThree(self)->int:
                """ This function returns 3 """
                return emulate()
            
        x = EmulateClass()
        ret = x.returntThree()
        assert ret == 3
        
    def test_FeatureClassMagicMethod(self, capsys):
        
        class EmulateClass:
            
            def __str__(self):
                """ This function returns "Hello World!" """
                return emulate()
            
        x = EmulateClass()
        print(x)
        stdout = capsys.readouterr()
        assert "Hello World!" in stdout.out
        
    def test_FeatureLocalVariables(self):
        
        def showLocals()->dict:
            """
            This function return in a dict all his locals variable and arguments.
            """
            local_1 = 42
            local_2 = "Hello World!"
            local_3 = [1, 2, 3, 4, 5]
            return emulate()
        
        ret_dict = {
            "local_1": 42,
            "local_2": "Hello World!",
            "local_3": [1, 2, 3, 4, 5]
        }
        ret = showLocals()
        assert ret == ret_dict
        
    # def test_FeatureModelInParamter(self):
    #     global g_apiKey
        
    #     my_model = config.Model(
    #         model="gpt-4o-mini",
    #         base_url="https://api.openai.com/v1/chat/completions",
    #         api_key=g_apiKey
    #     )
        
    #     def showModel()->str:
    #         """
    #         This function returns the LLm model (like "gpt-4o" or "llama-3-70b") with which it was emulated. It returns only the name used by its API.
    #         """
    #         return emulate(model=my_model)
        
    #     ret = showModel()
    #     assert ret == "gpt-4o-mini"
    
    def test_FeatureNestedFunction(self):
        
        def grandFunction():
            def returnHelloWorld():
                """ 
                This function returns "Hello World!".
                """
                return emulate()
            return returnHelloWorld
        
        nested = grandFunction()
        ret = nested()
        assert ret == "Hello World!"

class test_suggest:
    pass

class test_thought:
    pass

class test_config:
    pass


"""
pydantic
typing
model config
function called in another file or global
example
chain of thought 
cache
---
Test fonctionnel
test unitaire
test de performance
---
test en trompant le LLM dans la def ou la doc
Error:
quand func n'est pas trouvé, Erreur expliquant la déclaration dans le frame parent
def test():
    def a():
        \"\"\" Give me a ramdom word \"\""
        return emulate()
    return a

#Erreur
print(test()())
#Valid
b = test()
print(b())

CONTRIBUTING
changelog
doc
test
---
Makefile
make benchmark
make functests
make unittests
avec redirection de coverage et html dans TestData
argument makefile apiKey
"""