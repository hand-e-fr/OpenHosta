import pytest
import inspect
import re
import sys

from OpenHosta.core.inspector import HostaInspector as HI

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
        pass
    
    def test_FuncNotCallable(self):
        pass
    
class TestAttach:
    
    def test_OneAttr(self):
        pass
    
    def test_ManyAttr(self):
        pass
    
    def test_InvalidArgs(self):
        pass
    
    def test_BasicMethod(self):
        pass
    
    def test_InvalidMethod(self):
        pass
    
    def test_InvalidCallable(self):
        pass

