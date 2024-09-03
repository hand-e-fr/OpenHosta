import pytest
import time as t
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from OpenHosta import exec

class TestExec:
    
    def _exec_test(
        self,
        _function_def:str,
        _function_call:str,
        _function_return:str,
        *args,
        **kwargs
    ):
        return (_function_def, _function_call, _function_return, args, kwargs)
        