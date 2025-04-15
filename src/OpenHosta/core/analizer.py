
import inspect
from typing import _alias
from dataclasses import is_dataclass

def hosta_analyse_update(frame, analyse):
    args_info = inspect.getargvalues(frame)
    analyse["args"] = [{"name":a["name"], "value":args_info.locals[a["name"]], "type":a["type"]} for a in analyse["args"]] 
    return analyse

def hosta_analyze(frame, function_pointer):
    sig = inspect.signature(function_pointer)
    args_info = inspect.getargvalues(frame)
    
    result_args_value_table = [{
        "name":arg, 
        "value": args_info.locals[arg], 
        "type":sig.parameters[arg].annotation} for arg in args_info.args]
    

    result_function_name = function_pointer.__name__
    result_return_type = sig.return_annotation
    result_docstring = function_pointer.__doc__

    return {
        "name": result_function_name,
        "args": result_args_value_table,
        "type": result_return_type,
        "doc":  result_docstring
    }

def nice_type_name(obj) -> str:
    """
    Get a nice name for the type to insert in function description for LLM.
    """
    if type(obj) is _alias:
        t=obj.__repr__()
        t=t.replace("typing.", "")
        return t
    
    if hasattr(obj, "__name__"):
        return obj.__name__

    return str(obj)


def hosta_prompt_snippets(analyse):
    snippets = build_parameters_as_prompt(analyse["args"])

    snippets |= {
    "function_name"                  : analyse["name"],
    "function_return_as_python_type" : nice_type_name(analyse["type"]),
    "function_return_as_json_schema" : build_types_as_json_schema(analyse["type"]),
    "function_doc"                   : analyse["doc"],
    }

    python_call = "{function_name}({call_arguments})".format(**snippets)
    
    return snippets | {
        "function_call_as_python_code" : python_call,
    }

BASIC_TYPES = [
    int, float, complex, str, list, tuple, range, dict, set, frozenset,
    bool, bytes, bytearray, memoryview
]

def describe_specific_types(arg_type):
    # TODO: add pydantic types
    type_definition = None
    if arg_type in BASIC_TYPES or\
        type(arg_type) is _alias or\
            arg_type == type:
        print("Ignore type", arg_type)
        # This is generic type. Assume it is known. 
        pass

    elif is_dataclass(arg_type):
        type_definition=f"""\
python class {arg_type.__name__} is defines as a @dataclass:
{arg_type.__doc__}
"""       
    elif hasattr(arg_type, '__annotations__')  and \
            not arg_type.__annotations__ is inspect._empty:
        type_definition=f"""\
python class {arg_type.__name__} has this annotation:
{arg_type.__annotations__}
"""
    else:
        # Unknwon types
        pass #raise Exception(f"Unknwon type ({arg_type}). Please use another type.")

    return type_definition


def build_parameters_as_prompt(args):
    variable_definition_list = []
    type_definition_list = []
    inline_string_list = []
    call_string_list = []
    
    for a in args:
        name, value, arg_type = a["name"], a["value"], a["type"]
        str_arg = name
        call_arg = name
        if arg_type is inspect._empty:
            pass
        else:
            str_arg += ": "+nice_type_name(arg_type) 
            specifig_type_doc = describe_specific_types(arg_type)
            if not specifig_type_doc is None:
                type_definition_list.append(specifig_type_doc)

        # Place long variables outside function definition. 
        # math.pi is 17 char, I decide to cut at 20 
        str_value = repr(value)
        if len(str_value) > 20:
            variable_definition_list += [name+"="+str_value+"\n"]
        else:
            # We do not show default values as this could contradict values from call
            # str_arg += " = "+str_value
            call_arg += " = "+str_value

        inline_string_list += [str_arg]
        call_string_list   += [call_arg]

    return {
        "function_args":", ".join(inline_string_list),
        "call_arguments":", ".join(call_string_list), 
        "type_definitions":"\n".join(type_definition_list),
        "variable_declaration":"\n".join(variable_definition_list)
    }


def build_types_as_json_schema(arg_type):
    # TODO: build a JSON schema here
    return f"{describe_specific_types(arg_type)}"
