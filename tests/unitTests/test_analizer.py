import pytest
import inspect
import re
from typing import Optional, List, Union
from pydantic import DialogueModel, Field
from PIL import Image

from OpenHosta.core.analizer import FuncAnalizer as FA


class TestInspector:
    
    def test_InitSimple(self):
        def tmp():
            return inspect.currentframe()
        x = FA(tmp, tmp())
        assert type(x) == FA
        
    def test_InitInvalidArgs(self):
        with pytest.raises(AttributeError, match=re.escape("[_FuncInspector.__init__] Invalid arguments:\n'hi' is not a callable object")):
            FA("hi", 3)
            
    def test_FuncDef(self):
        def testfunc():
            return inspect.currentframe()
    
        frame = testfunc()
        x = FA(testfunc, frame)
        assert x.func_def.startswith("```")
        
    def test_FuncLocalsNoVal(self):
        def testfunc():
            return inspect.currentframe()
    
        frame = testfunc()
        x = FA(testfunc, frame)
        assert x.func_locals == (None, None)
        
    def test_FuncLocalsSimple(self):
        def testfunc():
            a = 2
            b = "hi"
            return inspect.currentframe()
    
        frame = testfunc()
        x = FA(testfunc, frame)
        assert x.func_locals == ({"a": 2, "b": "hi"}, None)

    def test_FuncLocalsSelf(self):
        class TMP:
            def __init__(self):
                self.c = 3.14
            
            def testfunc(self):
                a = 2
                b = "hi"
                return inspect.currentframe()
    
        tmp = TMP()
        frame = tmp.testfunc()
        x = FA(tmp.testfunc, frame)
        assert x.func_locals == ({"a": 2, "b": "hi"}, {"c": 3.14})
        
    def test_FuncCallSimple(self):
        def testfunc(a:int, b:str):
            return inspect.currentframe()
    
        frame = testfunc(2, "hi")
        x = FA(testfunc, frame)
        assert x.func_call == ("testfunc(a=2, b='hi')", {'a': 2, 'b': 'hi'})

    def test_FuncCallNoArgs(self):
        def testfunc():
            return inspect.currentframe()
    
        frame = testfunc()
        x = FA(testfunc, frame)
        assert x.func_call == ("testfunc()", {})
        
    def test_FuncCallComplexArgs(self):
        class TMP(DialogueModel):
            var:str = Field(default="", description="It's a var :)")
        def testfunc(a:TMP, b:Image):
            return inspect.currentframe()
    
        ins = TMP()
        img = Image.new('RGB', (10, 10), 'white')
        frame = testfunc(ins, img)
        x = FA(testfunc, frame)
        assert x.func_call == (f'testfunc(a={ins!r}, b={img!r})', {"a": ins, "b": img})
    
    def test_FuncTypeSimple(self):
        def testfunc(a:int, b:str)->list:
            return inspect.currentframe()
    
        frame = testfunc(2, "hi")
        x = FA(testfunc, frame)
        assert x.func_type == ([int, str], list)
        
    def test_FuncTypeArgsWithNoType(self):
        def testfunc(a, b):
            return inspect.currentframe()
    
        frame = testfunc(2, "hi")
        x = FA(testfunc, frame)
        assert x.func_type == ([inspect._empty, inspect._empty], None)
        
    def test_FuncTypeNoArgs(self):
        def testfunc():
            return inspect.currentframe()
    
        frame = testfunc()
        x = FA(testfunc, frame)
        assert x.func_type == ([], None)
        
    def test_FuncTypeComplexArgs(self):
        class TMP(DialogueModel):
            var:str = Field(default="", description="It's a var :)")
        def testfunc(a:TMP, b:Image)->Optional[List[int]]:
            return inspect.currentframe()
    
        ins = TMP()
        img = Image.new('RGB', (10, 10), 'white')
        frame = testfunc(ins, img)
        x = FA(testfunc, frame)
        assert x.func_type == ([type(ins), Image], Optional[List[int]])
        
    def test_FuncSchemaBuiltIn(self):
        def testfunc(a:int, b:int)->list:
            return inspect.currentframe()
        
        frame = testfunc(2, "hi")
        x = FA(testfunc, frame)
        assert x.func_schema == {'type': 'list'}
    
    def test_FuncSchemaAnnotated(self):
        def testfunc(a:Union[int, str])->Optional[List[float]]:
            return inspect.currentframe()
        
        frame = testfunc(2)
        x = FA(testfunc, frame)
        assert x.func_schema == {'anyOf': [{'items': {'type': 'number'}, 'type': 'array'}, {'type': 'null'}]}

    def test_FuncSchemaPydantic(self):
        class TMP(DialogueModel):
            var1:str = Field(default="", description="It's one var :)")
            var2:int = Field(default=0, description="It's two var :)")
        def testfunc(a:int)->TMP:
            return inspect.currentframe()
        
        frame = testfunc(2)
        x = FA(testfunc, frame)
        assert x.func_schema == {'properties': {'var1': {'default': '', 'description': "It's one var :)", 'title': 'Var1', 'type': 'string'}, 'var2': {'default': 0, 'description': "It's two var :)", 'title': 'Var2', 'type': 'integer'}}, 'title': 'TMP', 'type': 'object'}
    
    def test_FuncSchemaNoType(self):
        def testfunc():
            return inspect.currentframe()
        
        frame = testfunc()
        x = FA(testfunc, frame)
        assert x.func_schema == {'type': 'any'}
