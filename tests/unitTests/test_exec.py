import sys
import pytest
from unittest.mock import patch
import inspect

from OpenHosta import exec

class TestExtendScope:
    
    def test_basic(self):
        def printHello():
            print("Hello")

        x =  exec.HostaInjector(printHello)

        class Test:
            def test(self):
                return x._extend_scope()

        def caller():
            y = Test()
            return y.test()

        res = caller()
        assert res[0] == caller
        
    def test_Flask(self):
        from flask import Flask, request, session
        
        def printHello():
            print("Hello")

        x =  exec.HostaInjector(printHello)

        class Test:
            def test(self):
                return x._extend_scope()

        def caller():
            y = Test()
            return y.test()

        res = caller()
        del sys.modules["flask"]
        assert res[0] == caller
        
    def test_ErrorHandling(self):
        def printHello():
            print("Hello")

        x =  exec.HostaInjector(printHello)

        class Test:
            def test(self):
                return x._extend_scope()

        def caller():
            y = Test()
            return y.test()

        current = inspect.currentframe()
        print(f"INTERNAL: {current.f_locals}")
        current.f_locals["caller"] = "hello"
        current.f_locals.pop("caller")
        print(f"INTERNAL: {current.f_locals}")

        with patch("exec.hasattr", return_value=False):
            res = caller()
        assert res == caller