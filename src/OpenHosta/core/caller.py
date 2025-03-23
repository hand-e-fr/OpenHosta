from typing import Callable, Optional, Union, Tuple
from types import FrameType, MethodType, FunctionType

import inspect

from OpenHosta.utils.errors import FrameError
import sys

def identify_function_of_frame(function_frame):
    """
    frame -> code -> function

    We need to find the function pointer in order to store OpenHosta inspection object
    The main advantage over a centralized list is that this object will be deleted 
    a the same time than the associated function. Keeping a centrelized list would
    induce deletion issues.

    """
    
    function_code = function_frame.f_code
    function_name = function_frame.f_code.co_name
    function_pointer = None # This is to be found by the code below

    # First we look in every parent frame if the function exists there

    look_for_function_in_frame = function_frame.f_back
    while isinstance(look_for_function_in_frame, FrameType):
        
        for candidate_obj in look_for_function_in_frame.f_locals.values():
            # Use try catch as With Flask we found some strange behaviors for some candidate_obj
            try:
                # This is in case function exists in the caller stack
                if callable(candidate_obj) and hasattr(candidate_obj, "__code__"):
                    if candidate_obj.__code__ is function_code:
                        function_pointer = candidate_obj
                        break

            except Exception as e:
                raise FrameError("This is the strange error with Flask", e)
        
        look_for_function_in_frame = look_for_function_in_frame.f_back
    
    # Then look at the object in case we are a method of class
    if function_pointer is None:
        args_info = inspect.getargvalues(function_frame)
        if len(args_info.args) > 0:

            # first_arg_name should be 'self', 'cls' or any funny names)
            first_arg_name = args_info.args[0]
            
            # We get the first argument and check if is is a class 
            first_argument = args_info.locals[first_arg_name]
            
            # If the class has an attribute with our name, there is a good chance it is us
            bound_function = getattr(first_argument, function_name, None)
            if bound_function:
                if isinstance(bound_function, MethodType):
                    function_pointer = bound_function.__func__
                else:
                    # If function is a @staticmethod it does not have class as 
                    # first argument. But it was found by last part below.
                    pass

    # Finally we look in every parent frame if an object has the function
    # This is mainly for @staticmethod

    look_for_function_in_frame = function_frame.f_back
    while isinstance(look_for_function_in_frame, FrameType):
        
        for candidate_obj in look_for_function_in_frame.f_locals.values():
            # Use try catch as With Flask we found some strange behaviors for some candidate_obj
            try:
                # This is in case function was declared as @staticmethod
                if callable(candidate_obj) and hasattr(candidate_obj, function_name):
                    candidate_function = getattr(candidate_obj, function_name)
                    if isinstance(candidate_function, FunctionType) and \
                        candidate_function.__code__ is function_code:
                        function_pointer = candidate_function
                        break

            except Exception as e:
                raise FrameError("This is the strange error with Flask", e)
        
        look_for_function_in_frame = look_for_function_in_frame.f_back

    # Try in globals if not found in parent frames 
    if function_pointer is None:
        function_pointer = function_frame.f_globals.get(function_name, None)
    
    # In case there is a wrapper for class or global defined function
    if not function_pointer is None:
        function_pointer = inspect.unwrap(function_pointer) 

    if not function_pointer is None and \
       not function_pointer.__code__ is function_code:
        raise FrameError(f"We thought that we had found {function_name} but it is not the good one!")

    if function_pointer is None:
        raise Exception("Unable to find function for inspection")

    return function_pointer


def get_caller_frame():
    try:
        frame = sys._getframe(2)
    except ValueError as e:
        raise FrameError("get_caller_frame shall not be called from outsite of exec functions")
    
    return frame

def hosta_analyze(frame, function_pointer):
    analyse = {}
    sig = inspect.signature(function_pointer)
    args_info = inspect.getargvalues(frame)
    args_values = {arg: args_info.locals[arg] for arg in args_info.args}
    analyse["args_values"] = args_values
    # func_name = getattr(self.function_pointer, "__name__")
    # func_params = ", ".join(
    #     [
    #         (
    #             f"{param_name}: {nice_type_name(param.annotation)}"
    #             if param.annotation != inspect.Parameter.empty
    #             else param_name
    #         )
    #         for param_name, param in self.sig.parameters.items()
    #     ]
    # )
    # if self.sig.return_annotation is inspect.Signature.empty:
    #     func_return = ""
    # else:
    #     func_return = " -> " + nice_type_name(self.sig.return_annotation)

    # definition = (
    #     f"```python\ndef {func_name}({func_params}){func_return}:\n"
    #     f"    \"\"\"{self.function_pointer.__doc__}\"\"\"\n    ...\n```"
    # )    
    return analyse

def hosta_inspect(frame):
    
    return {
        "args_values":args_values,
        "frame":frame} 

def get_hota_inspection(frame):
    function_pointer = identify_function_of_frame(frame)  
    inspection = getattr(function_pointer, "hosta_inspection", None)
    
    if inspection == None:
        inspection = hosta_inspect(frame)
        setattr(function_pointer, "hosta_inspection", inspection)

    return inspection


def emulate():
    frame = get_caller_frame()
    inspection = get_hota_inspection(frame)
    
    params = ", ".join([f"{k}={v}" for k,v in inspection["args_values"].items()])
    s = f"{function_pointer.__name__}({params})"
    return(s)


### get_caller_function has to work with:
# - functions, 
# - objects methods, 
# - docorated function
# - decorated method
# - functions in functions, 
# - flask routed functions

# It returns:
# - the function pointer with its original name
# - the collable object that is used to reach this function (binder, wrapper, decorator, ...)

### function:
# - function pointer equals binder

def my_function(b, arg, *, dd, fd=5, toto=44):
    return emulate()

my_function(44, "rr", dd=4)

toto=my_function
toto(45, "rdsd", dd=4)

### Object Method

class MyClass:
    def methode_instance(self, b, arg, *, dd, fd=5, toto=44):
        return emulate()
    
    @staticmethod
    def staticmethod(b, arg, *, dd, fd=5, toto=44):
        return emulate()
    
    @classmethod
    def classmethod(cls, b, arg, *, dd, fd=5, toto=44):
        return emulate()
    
    def call_toto(self):
        return toto(45, "rdsd", dd=4)
    
    
mc = MyClass()
mc.methode_instance(45, "es", dd=5)
mc.staticmethod(45, "es", dd=5)
MyClass.staticmethod(45, "es", dd=5)
mc.classmethod(45, "es", dd=5)
MyClass.classmethod(45, "es", dd=5)

mc.call_toto()


### functions in functions

def foo(x=6):
    def foobar(val):
        return emulate()
    
    def bar(a=4):
        return foobar(a)
    return bar(x)

foo("f")

## Flask

from flask import Flask

app = Flask(__name__)

@app.route('/<page>')
def home(page=3):
    return emulate()


if __name__ == '__main__':
    app.run(debug=True)
