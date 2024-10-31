import pytest
import inspect
import re
import sys
from unittest.mock import patch

from OpenHosta.core.inspector import HostaInspector as HI
from OpenHosta.utils.errors import FrameError

class TestExtend:
    
    def test_BasicMethod(self):
        class TMP:
            def tmp_extend(self):
                return HI._extend()
        def tmp():
            x = TMP()
            return x.tmp_extend()
        def tmp2():
            return (tmp(), inspect.currentframe())
        
        res = tmp2()
        assert res[0] == (tmp2, res[1])
        
    def test_BasicFunc(self):
        pass
        
    def test_LowBackLevel(self):    
        def tmp():
            return (HI._extend(back_level=1), inspect.currentframe())
        
        res = tmp()
        
        assert res[0] == (tmp, res[1])
        
    def test_InvalidArgs(self):
        with pytest.raises(ValueError, match=re.escape("[HostaInspector._extend] back_level must a non-zero positive integers.")):
            HI._extend(back_level=0)
            HI._extend(back_level=-1)
            HI._extend(back_level="Hi mom")
    
    def test_FuncWithFlask(self):
        from flask import Flask, request, session

        def tmp():
            return (HI._extend(back_level=1), inspect.currentframe())
        
        res = tmp()
        del sys.modules["flask"]
        assert res[0] == (tmp, res[1])

    def test_FuncWithGlobals(self):
        pass
    
    def test_FBackNotFound(self):
        with pytest.raises(FrameError, match=re.escape("[HostaInspector._extend] Frame can't be found (level: 33)")):
            HI._extend(back_level=100)
    
    def test_FuncNotCallable(self):
        pass
    
class TestAttach:
    
    def test_OneAttr(self):
        def tmp():
            return
        HI._attach(tmp, {"nb": 3})
        assert tmp.nb == 3
            
    def test_ManyAttr(self):
        def tmp():
            return
        HI._attach(tmp, {
            "a": 1,
            "b": "hi",
            "c": tmp
        })
        assert tmp.a == 1
        assert tmp.b == "hi"
        assert tmp.c == tmp
    
    def test_InvalidArgs(self):
        def tmp():
            return
        with pytest.raises(ValueError, match=re.escape("[HostaInspector._attach] Invalid arguments")):
            HI._attach(tmp, "6")
            HI._attach("a", 1)
    
    def test_BasicMethod(self):
        class TMP:
            def tmp(self):
                return
        x = TMP()
        HI._attach(x.tmp, {"a": 1})
        assert x.tmp.a == 1
    
    def test_InvalidMethod(self):
        def tmp():
            return
        with patch('inspect.ismethod', return_value=True):
            with pytest.raises(AttributeError, match=re.escape("[HostaInspector._attach] Failed to attach attributs. \"__func__\" attribut is missing.")):
                HI._attach(tmp, {"a": 1})
    
    def test_InvalidCallable(self):
        class TMP:
            pass
        with pytest.raises(AttributeError, match=re.escape(f"[HostaInspector._attach] Failed to attach attributs. Object's type not supported: {type(TMP)}.")):
            HI._attach(TMP, {"a": 1})

