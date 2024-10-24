import pytest
import time as t
from pydantic import BaseModel
from typing import Callable
import numpy as np

import OpenHosta.OpenHosta
import OpenHosta.config as config
from OpenHosta.emulate import emulate
from OpenHosta.example import example

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

class User(BaseModel):
    name: str
    email: str
    age: int

# class TestPredict:
#     def test_basic_input_predict(self):
#         def predict_1(a: int) -> float:
#             """
#             This function predicts the id of a letter
#             """
#             example(1, hosta_out=1.0)
#             example(2, hosta_out=2.0)
#             example(3, hosta_out=3.0)
#             return predict()
        
#         ret_1 = predict_1(1)
#         assert type(ret_1) == float


#     def test_mutiple_input_predict(self):
#         def predict_2(a: int, b:int) -> float:
#             """
#             This function predict the id of sum of two letter
#             """
#             example(a=1, b=2, hosta_out=3.0, hosta_func=predict_2)
#             return predict()
#         ret_2 = predict_2(1, 2)
#         assert type(ret_2) == float

#     def test_attributs_predict(self, capsys):
#         def predict_3(a:int) -> float:
#             """
#             transform an int into a float
#             """
#             example(1, hosta_out=1.0)
#             return predict()

#         ret = predict_3(1)
#         predict_3.retrain(epochs=15, verbose=False)
#         ret_after = predict_3(1)
#         assert ret != ret_after

#         ret_emulate = predict_3.emulate(1)
#         print(ret_emulate)
#         assert type(ret_emulate) == float

#         predict_3.continue_train(epochs=1500, get_loss=0.01, verbose=True)
#         stdout = capsys.readouterr()
#         assert "Loss target achieved at epoch" in stdout.out

# class TestTrainingset:
#     def test_training_function(self):
#         len_sublist = 0
#         def function_to_test(a: int, b: int) -> float:
#             """
#             This function returns the sum of two integers.
#             """
#             return predict()
#         example(a=1, b=2, hosta_out=3.0, hosta_func=function_to_test)

#         training_test = TrainingSet(function_to_test)
#         training_test.add(a=2, b=3, hosta_out=5.0)
#         dataset = training_test.visualize()

#         expected_values = [{'a': 1, 'b': 2, 'hosta_out': 3}, {'a': 2, 'b': 3, 'hosta_out': 5}]

#         for expected in expected_values:
#             assert expected in dataset[0] or expected in dataset[1], f"{expected} n'est pas présent dans le dataset"

class TestEmulate:
       
    def test_FeatureModelInParameter(self):
        global g_apiKey
        
        abracadabra = config.Model(
            model="gpt-4o-mini",
            base_url="https://api.openai.com/v1/chat/completions",
            api_key=g_apiKey
        )
        
        def randomSentence()->str:
            """
            This function returns a random sentence.
            """
            return emulate(model=abracadabra)
        
        ret = randomSentence()
        ret_model = randomSentence._last_response["model"]
        print(ret_model)
        assert "gpt-4o-mini" in ret_model   
       
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

class TestThought:
    
    def test_BasicDirect(self):
        ret = thought("Multiply by 2")(8)
        assert ret == 16
    
    def test_BasicIndirect(self):
        x = thought("Translate in English")
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
        ret = thought(prompt)(args)
        assert isinstance(ret, expected)
        
    @pytest.mark.parametrize("prompt, args, expected", [
        ("Count the letter un a setence", "Hello World!", int),
        ("capitalize a setence", "hello world!", str),
        ("Give the number Pi to 3 decimal places", "", float),
        ("Sort in ascending order", [2, 5, 1, 12, 6], list),
        ("Is a positive number", 6, bool),
    ])
    def test_FeaturePredict(self, prompt, args, expected):
        x = thought(prompt)
        ret = x(args)
        assert x._return_type is expected

    def test_FeatureMultiArgs(self):
        x = thought("Combine each word of a sentence in a string")
        ret = x("Hello", ", how are you ?", " Nice to meet you !")
        assert ret == "Hello, how are you ? Nice to meet you !"
    
    def test_FeatureChainOfThought(self):
        pass
    
    def test_FeatureDefaultModel(self):
        my_model = config.Model(
            model="gpt-4o-mini",
            base_url="https://api.openai.com/v1/chat/completions",
            api_key=g_apiKey
        )
        
        config.set_default_model(my_model)
        
        x = thought("Is a masculine name")
        ret = x("Max")
        print(x._last_response)
        ret_model = x._last_response["model"]
        assert ret == True
        assert "gpt-4o-mini" in ret_model
    
    def test_FeatureCachedPrediction(self):
        pass
class TestTypingPydantic:
    pass