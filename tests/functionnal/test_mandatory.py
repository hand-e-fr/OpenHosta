from OpenHosta.pipelines.simple_pipeline import OneTurnConversationPipeline
import pytest
# -*- coding: utf-8 -*-

#########################################################
#
# Test model configuration
#
#########################################################

import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# To run these tests you need to set .env variables to define an LLM provider
# e.g. for OpenAI:
# OPENHOSTA_LLM_PROVIDER=openai
# OPENHOSTA_OPENAI_API_KEY=your_api_key

# you also need to install pytest and python-dotenv:
# pip install pytest python-dotenv

# To run the tests, use the command:
# pytest OpenHosta/tests/functionnalTests/test_ask.py


from OpenHosta.utils.import_handler import is_pydantic_available
assert is_pydantic_available, "Pydantic shall be installed"

import os
from pydantic import BaseModel
from typing import Callable

from OpenHosta import config, emulate

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
       
    from OpenHosta.pipelines.simple_pipeline import OneTurnConversationPipeline
    def test_FeatureModelInParameter(self):
        abracadabra = config.OpenAICompatibleModel(
            model_name="gpt-4o",
            base_url="https://api.openai.com/v1/chat/completions",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        my_pipe = OneTurnConversationPipeline(model_list=[abracadabra])
        my_pipe.user_call_meta_prompt.source = "This is the python call:\n"+my_pipe.user_call_meta_prompt.source
        
        def randomSentence()->str:
            """
            This function returns a random sentence.
            """
            return emulate(pipeline=my_pipe)
        
        ret = randomSentence()
        ret_model = randomSentence.hosta_inspection["model"]
        print(ret_model)
        assert "gpt-4o" in ret_model.model_name 


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
            
            def __str__(self) -> str:
                """ This function returns "Hello World!" """
                return emulate()
            
        x = EmulateClass()
        print(x)
        stdout = capsys.readouterr()
        assert "Hello World!" in stdout.out
        
    # TODO: decide if we keep this test or not
    def test_FeatureLocalVariables(self):
        
        def showLocals()->dict:
            """
            This function return in a dict all his locals variable and arguments.
            """
            local_1 = 42
            local_2 = "Hello World!"
            local_3 = [1, 2, 3, 4, 5]
            return emulate()
            # return emulate(use_locals=True)
        
        ret_dict = {
            "local_1": 42,
            "local_2": "Hello World!",
            "local_3": [1, 2, 3, 4, 5]
        }
        ret = showLocals()
        assert ret == ret_dict
      
    def test_FeatureNestedFunction(self):
            
            def grandFunction():
                def returnHelloWorld()->str:
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

from OpenHosta import closure

class TestClosure:
    
    def test_BasicDirect(self):
        ret = closure("Multiply this number by 2")(8)
        assert ret == 16
    
    def test_BasicIndirect(self):
        x = closure("Translate in English")
        ret = x("Bonjour Monde!")
        assert isinstance(x, Callable)
        assert ret == "Hello World!"

    @pytest.mark.parametrize("prompt, args, expected", [
        ("return a random integer", "", int),
        ("return a random sentence", "", str),
        ("return a random float", "", float),
        ("return a list of 5 random integers", "", list),
        ("return a random bool in python", "", bool),
    ])
    def test_BasicTyped(self, prompt, args, expected):
        ret = closure(prompt)(args)
        assert type(ret) is expected
        

    def test_FeatureMultiArgs(self):
        x = closure("Combine each part of sentence in a signle string")
        ret = x("Hello", "how are you?", "Nice to meet you!")
        assert "ello" in ret and "are" in ret and "meet" in ret
    
    def test_FeatureChainOfclosure(self):
        pass
    
    def test_FeatureCachedPrediction(self):
        pass

from OpenHosta import test
    
class TestTestMandatory:
    
    def test_BasicMandatory(self):
        name = "Louis"
        if test(f"Is '{name}' a name ?"):
            result = f"Yes, {name} is a name"
        else:
            result = f"No, {name} is not a name"
        assert result.startswith("Yes"), "Louis should be recognized as a name"
        
        