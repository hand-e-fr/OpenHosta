
import inspect
from ..models import ModelCapabilities
from ..core.type_converter import nice_type_name, describe_type_as_python, describe_type_as_schema, BASIC_TYPES

def hosta_analyze_update(frame, inspection):
    analyse = inspection["analyse"]
    new_analyse = {
        "name": analyse["name"],
        "args": [],
        "type": analyse["type"],
        "doc":  analyse["doc"]
    }
    args_info = inspect.getargvalues(frame)
    new_analyse["args"] = [{"name":a["name"], "value":args_info.locals[a["name"]], "type":a["type"]} for a in analyse["args"]] 
    return new_analyse

def hosta_analyze(frame=None, function_pointer=None):
    sig = inspect.signature(function_pointer)

    if frame is None:
        result_args_value_table = []
    else:
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


def encode_function(analyse, model_capability=set([ModelCapabilities.TEXT2TEXT])):
    """
    Encode the function signature and docstring into a format suitable for the model.
    """
    snippets  = {}
    snippets |= encode_function_documentation(analyse)
    snippets |= encode_function_parameter_types(analyse)
    snippets |= encode_function_parameter_values(analyse)
    snippets |= encode_function_parameter_names(analyse)
    snippets |= encode_function_return_type(analyse)
    snippets |= encode_function_return_type_definition(analyse)
    
    return snippets

def encode_function_documentation(analyse):
        return {
            "function_name" : analyse["name"], 
            "function_doc"  : analyse["doc"],
            }

def encode_function_parameter_types(analyse):
    
    # Types of the arguments when type definition is too long
    # to be included inline in the function call
    json_schema_types_definition_list = {}    
    
    # Types of the arguments when type definition is too long
    # to be included inline in the function call
    python_types_definition_list = {}    
    
    for a in analyse["args"]:
        arg_type = a["type"]
        if arg_type is inspect._empty or arg_type in BASIC_TYPES:
            # Basic types are assumed to be known by the model
            # and are not included in the prompt
            pass
        else:
            specifig_type_doc = describe_type_as_python(arg_type)
            if not specifig_type_doc is None:
                python_types_definition_list[nice_type_name(arg_type)] = specifig_type_doc
                
            specifig_type_json = describe_type_as_schema(arg_type)
            if not specifig_type_json is None:
                json_schema_types_definition_list[nice_type_name(arg_type)] = specifig_type_json

    return {
        "python_type_definition_dict":       "\n".join([f"```python\n# definition of type {k}:\n{v}\n```" for k,v in python_types_definition_list.items()]),
        "json_schema_type_definition_dict":  "\n\n".join([f"# JSON Schema of type {k}:\n```json\n{v}\n```" for k,v in json_schema_types_definition_list.items()]),
    }

def encode_function_parameter_values(analyse):

    args = analyse["args"]
    
    # Vaiable value definition when content is too long
    # to be included inline in the function call
    variable_definition_list = []
    
    # Call arguments for inline function call
    call_string_list = []
    
    for a in args:
        call_arg, value, arg_type = a["name"], a["value"], a["type"]

        # Place long variables outside function definition. 
        # math.pi is 17 char, I decide to cut at 20 
        str_value = repr(value)
        if len(str_value) > 20:
            try:
                import PIL
                if isinstance(value, PIL.Image.Image):
                    # Add a comment to explain that the image content is in the message
                    str_value += f" # the real content of `{call_arg}` image is provided as an image in the message"
            except:
                # PIL is not available. It cannot be an image
                pass
            variable_definition_list += [call_arg+"="+str_value+"\n"]
        else:
            # We do not show default values as this could contradict values from call
            # call_arg += " = "+str_value
            call_arg += " = "+str_value
        
        call_string_list += [call_arg]
        
    return {
        "variables_initialization":"\n\n".join(variable_definition_list),
        "function_call_arguments":", ".join(call_string_list),
    }

def encode_function_parameter_names(analyse):

    args = analyse["args"]
    
    # Inline argument names and typing if short enough
    inline_string_list = []

    # Vaiable value definition when content is too long
    # to be included inline in the function call
    variable_definition_list = []
    
    for a in args:
        str_arg, arg_type = a["name"], a["type"]
        if arg_type is inspect._empty:
            pass
        else:
            str_arg += ": "+nice_type_name(arg_type) 

        inline_string_list += [str_arg]


    return {
        "function_return_type": " -> " + nice_type_name(analyse["type"]) if analyse["type"] else "",
        "function_args":", ".join(inline_string_list),
        "function_inline_variable_declaration":"\n".join(variable_definition_list),
    }


def encode_function_return_type(analyse):
    return {
        "function_return_type": analyse["type"],
        "function_return_type_name": nice_type_name(analyse["type"]),
    }
    
def encode_function_return_type_definition(analyse):

    return {
        "function_return_as_python_type" : describe_type_as_python(analyse["type"]),
        "function_return_as_json_schema" : describe_type_as_schema(analyse["type"]),
        }
    