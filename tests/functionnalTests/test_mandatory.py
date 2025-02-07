import pytest
import os
from pydantic import BaseModel
from typing import Callable

from OpenHosta import config, emulate, thinkof

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

class User(BaseModel):
    name: str
    email: str
    age: int

class TestEmulate:
       
    def test_FeatureModelInParameter(self):
        abracadabra = config.Model(
            model="gpt-4o",
            base_url="https://api.openai.com/v1/chat/completions",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        def randomSentence()->str:
            """
            This function returns a random sentence.
            """
            return emulate(model=abracadabra)
        
        ret = randomSentence()
        ret_model = randomSentence._last_response["response_dict"]["model"]
        print(ret_model)
        assert "gpt-4o" in ret_model   
       
    @pytest.mark.parametrize("type, name, doc, arg, expected", [
        ("str", "generator", "generates a sentence", "", str),
        ("int", "generator", "generates an integer", "", int),
        ("list", "generator", "generates a list in python", "", list),
        ("float", "generator", "generates a float in python", "", float),
    ])
    def test_basicType(self, type, name, doc, arg, expected):
        def generator():
            """
            """
            return emulate()
        generator.__doc__ = doc
        generator.__name__ = name
        generator.__annotations__ = {'return':expected}
        result = generator()
        assert isinstance(result, expected)


    def test_FeaturesEmptyInfos(self):
        def a():
            return emulate()
        res = a()
        assert res is None
        
    def test_FeatureDecorator(self):
        
        def decorator(function_pointer):
            def wrapper(*args, **kwargs):
                res = function_pointer(*args, **kwargs)
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
            return emulate(use_locals_as_ctx=True)
        
        ret_dict = {
            "local_1": 42,
            "local_2": "Hello World!",
            "local_3": [1, 2, 3, 4, 5]
        }
        ret = showLocals()
        assert ret == ret_dict
      
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
        
    def test_FeaturePydanticGlobal(self):
            
        def generateAccount(name:str, email:str, age:int)->User:
            """
            This function generates a customer account with information based on the arguments passed, and returns it to the pydantic “User” model.
            """
            return emulate()
        
        ret = generateAccount("Max", "maxexample@gmail.com", 21)
        ex = User(name="Max", email="maxexample@gmail.com", age=18)
        assert type(ret) is User
        
    def test_FeaturePydanticLocal(self):
        pass
        
    def test_rc2(self):
        
        def multiply(a:int, b:int)->int:
            """
            This function multiplies two integers in parameter.
            """
            return emulate()
        
        def main():
            return multiply(2 ,3)
            
        res = main()
        assert res == 6

class Testthinkof:
    
    def test_BasicDirect(self):
        ret = thinkof("Multiply this number by 2")(8)
        assert ret == 16
    
    def test_BasicIndirect(self):
        x = thinkof("Translate in English")
        ret = x("Bonjour Monde!")
        assert isinstance(x, Callable)
        assert ret == "Hello World!"

    @pytest.mark.parametrize("prompt, args, expected", [
        ("return a random integer", "", int),
        ("return a random sentence", "", str),
        ("return a random float", "", float),
        ("return list with 5 random integers", "", list),
        ("return a random bool in python", "", bool),
    ])
    def test_BasicTyped(self, prompt, args, expected):
        ret = thinkof(prompt)(args)
        assert isinstance(ret, expected)
        
    @pytest.mark.parametrize("prompt, args, expected", [
        ("Count the letter un a setence", "Hello World!", int),
        ("capitalize a setence", "hello world!", str),
        ("Give the number Pi to 3 decimal places", "", float),
        ("Sort in ascending order", [2, 5, 1, 12, 6], list),
        ("Is a positive number", 6, bool),
    ])
    def test_FeaturePredict(self, prompt, args, expected):
        x = thinkof(prompt)
        ret = x(args)
        assert x._infos.f_type[1] is expected

    def test_FeatureMultiArgs(self):
        x = thinkof("Combine each part of sentence in a signle string")
        ret = x("Hello", "how are you?", "Nice to meet you!")
        assert "ello" in ret and "are" in ret and "meet" in ret
    
    def test_FeatureChainOfthinkof(self):
        pass
    
    # def test_FeatureDefaultModel(self):
    #     my_model = config.Model(
    #         model="gpt-4o-mini",
    #         base_url="https://api.openai.com/v1/chat/completions",
    #         api_key=g_apiKey
    #     )
        
    #     config.set_default_model(my_model)
        
    #     x = thinkof("Is a masculine name")
    #     ret = x("Max")
    #     print(x._last_response)
    #     ret_model = x._last_response["response_dict"]["model"]
    #     assert ret == True
    #     assert "gpt-4o-mini" in ret_model
    
    def test_FeatureCachedPrediction(self):
        pass