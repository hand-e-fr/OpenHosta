import sys
import inspect

from types import FrameType, MethodType, FunctionType

from ..utils.errors import FrameError
from .analizer import hosta_analyze, hosta_analyze_update

type Inspection = dict

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

def get_hosta_inspection(frame=None, function_pointer=None):
    if function_pointer is None:
        function_pointer = identify_function_of_frame(frame)
    else:
        function_pointer = function_pointer
    
    inspection = getattr(function_pointer, "hosta_inspection", None)
    
    if inspection == None:
        analyse = hosta_analyze(frame, function_pointer)
        inspection = {
            "function":function_pointer,
            "frame": frame,
            "analyse": analyse,
            "logs": {},
            "counters": {},
            "prompt_data":{},
            "pipe": None
        }
        setattr(function_pointer, "hosta_inspection", inspection)
    else:
        if frame is None:
            # We do not have argument types from the call (most likely a closure)
            inspection["analyse"]["args"] = [] 
        else:
            analyse = hosta_analyze_update(frame, inspection)
            inspection["analyse"] = analyse
        inspection["frame"] = frame

    return inspection

def get_last_frame(function_pointer):
    """
    Find the last frame of an Hosta function.
    This is usefull when debugging prompts.

    If the function was never called, return None.
    """

    inspection = getattr(function_pointer, "hosta_inspection", None)

    if inspection == None:
        frame = None
    else:
        frame = inspection["frame"]

    return frame