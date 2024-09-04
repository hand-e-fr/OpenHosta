import sys

from emulate import _exec_emulate 

def thought(key):
    _function_infos = {
        "function_def": "",
        "function_call": "",
        "return_type": None,
    }
    def inner_func(*args, **kwargs):
        try:
            _function_infos["function_def"] = key
            _function_infos["function_call"] = str(args[0])
            result = _exec_emulate(_function_infos)
        except Exception as e:
            sys.stderr.write(Exception)
            sys.stderr.write("[LMDA_ERROR]")
            result = None
        return result

    return inner_func
