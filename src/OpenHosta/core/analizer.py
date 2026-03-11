
import inspect

from dataclasses import dataclass, field
from typing import Any, List, Optional, Union

from ..core.base_model import ModelCapabilities
from ..guarded.resolver import TypeResolver

@dataclass
class AnalyzedArgument:
    name: str
    value: Any
    type: Any

@dataclass
class AnalyzedFunction:
    name: str
    args: List[AnalyzedArgument]
    type: Any
    doc: Optional[str]

def _extract_enums_from_guarded(guarded_type, seen_enums=None) -> str:
    if seen_enums is None:
        seen_enums = set()
    
    enums_doc = ""
    
    # If it's a GuardedEnum, document its members
    if hasattr(guarded_type, "_members") and guarded_type not in seen_enums:
        seen_enums.add(guarded_type)
        enum_name = getattr(guarded_type, "__name__", "Enum")
        if enum_name.startswith("Guarded_"):
            enum_name = enum_name[8:]
        members_str = ", ".join(guarded_type._members.keys())
        enums_doc += f"Where {enum_name} values can be: {members_str}\n"

    # Recursively check inner types if it's a generic collection
    inner_types = []
    
    # Standard Generics
    if hasattr(guarded_type, "__args__"): 
        inner_types.extend(guarded_type.__args__)
        
    # Guarded Collections
    if hasattr(guarded_type, "_item_type"): # GuardedList, GuardedSet
        inner_types.append(guarded_type._item_type)
    if hasattr(guarded_type, "_item_types"): # GuardedTuple
        if isinstance(guarded_type._item_types, (list, tuple)):
            inner_types.extend(guarded_type._item_types)
    if hasattr(guarded_type, "_key_type"): # GuardedDict
        inner_types.append(guarded_type._key_type)
    if hasattr(guarded_type, "_value_type"): # GuardedDict
        inner_types.append(guarded_type._value_type)

    for inner in inner_types:
        try:
            # We must be careful because inner might be a python type not yet resolved
            resolved_inner = TypeResolver.resolve(inner)
            enums_doc += _extract_enums_from_guarded(resolved_inner, seen_enums)
        except Exception:
            pass
            
    return enums_doc

def describe_type_as_python(p_type) -> str:
    """
    Returns the English description of the type using Guarded TypeResolver.
    """
    if p_type is None or p_type is inspect._empty:
        return ""
    
    try:
        guarded_type = TypeResolver.resolve(p_type)
        desc = ""
        if hasattr(guarded_type, "_type_en") and guarded_type._type_en:
            desc = guarded_type._type_en
            
        enum_details = _extract_enums_from_guarded(guarded_type)
        if enum_details:
            desc += "\n" + enum_details.strip()
            
        if desc:
            return desc
    except Exception as e:
        # Fallback if resolution fails
        pass
    
    return str(p_type)

                

def is_typing_type(arg_type):
    # Check if the type provided as argument exist in typing library
    return str(arg_type).startswith("typing.")

def nice_type_name(p_type) -> str:
    """
    Get a nice name for the type to insert in function description for LLM.
    """
    if is_typing_type(p_type):
        t=repr(p_type)
        t=t.replace("typing.", "")
        return t
    
    if hasattr(p_type, "__name__"):
        return p_type.__name__

    return str(p_type)

def hosta_analyze_update(frame, analyse: AnalyzedFunction) -> AnalyzedFunction:
    args_info = inspect.getargvalues(frame)
    
    new_args = []
    for a in analyse.args:
        new_args.append(AnalyzedArgument(
            name=a.name,
            value=args_info.locals.get(a.name, a.value),
            type=a.type
        ))

    return AnalyzedFunction(
        name=analyse.name,
        args=new_args,
        type=analyse.type,
        doc=analyse.doc
    )

def hosta_analyze(frame=None, function_pointer=None) -> AnalyzedFunction:
    sig = inspect.signature(function_pointer)

    result_args_value_table = []
    if frame is not None:
        args_info = inspect.getargvalues(frame)
        for arg in args_info.args:
            result_args_value_table.append(AnalyzedArgument(
                name=arg,
                value=args_info.locals[arg],
                type=sig.parameters[arg].annotation
            ))
    else:
        for name, param in sig.parameters.items():
            result_args_value_table.append(AnalyzedArgument(
                name=name,
                value=inspect._empty,
                type=param.annotation
            ))
    
    result_function_name = function_pointer.__name__
    result_return_type = sig.return_annotation
    result_docstring = function_pointer.__doc__

    return AnalyzedFunction(
        name=result_function_name,
        args=result_args_value_table,
        type=result_return_type,
        doc=result_docstring
    )


def encode_function(analyse: AnalyzedFunction, model_capability=set([ModelCapabilities.TEXT2TEXT])):
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

def encode_function_documentation(analyse: AnalyzedFunction):
        return {
            "function_name" : analyse.name, 
            "function_doc"  : analyse.doc,
            }

def encode_function_parameter_types(analyse: AnalyzedFunction):
    
    
    # Types of the arguments when type definition is too long
    # to be included inline in the function call
    python_types_definition_list = {}    
    
    for a in analyse.args:
        arg_type = a.type
        specifig_type_doc = describe_type_as_python(arg_type)
        if specifig_type_doc:
            python_types_definition_list[nice_type_name(arg_type)] = specifig_type_doc
            
    # Include the return type too, as it might contain Enums we need to document
    if analyse.type is not None and analyse.type is not inspect._empty:
        specifig_type_doc = describe_type_as_python(analyse.type)
        if specifig_type_doc:
            python_types_definition_list["Return Type " + nice_type_name(analyse.type)] = specifig_type_doc
                
    return {
        "python_type_definition_dict":       "\n".join([f"```python\n# definition of type {k}:\n{v}\n```" for k,v in python_types_definition_list.items()])
    }

def encode_function_parameter_values(analyse: AnalyzedFunction):

    args = analyse.args
    
    # Vaiable value definition when content is too long
    # to be included inline in the function call
    variable_definition_list = []
    
    # Call arguments for inline function call
    call_string_list = []
    
    for a in args:
        call_arg, value, arg_type = a.name, a.value, a.type
        
        # Don't try to format _empty values
        if value is inspect._empty:
            continue

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

def encode_function_parameter_names(analyse: AnalyzedFunction):

    args = analyse.args
    
    # Inline argument names and typing if short enough
    inline_string_list = []

    # Vaiable value definition when content is too long
    # to be included inline in the function call
    variable_definition_list = []
    
    for a in args:
        str_arg, arg_type = a.name, a.type
        if arg_type is inspect._empty:
            pass
        else:
            str_arg += ": "+nice_type_name(arg_type) 

        inline_string_list += [str_arg]


    return {
        "function_return_type": " -> " + nice_type_name(analyse.type) if analyse.type else "",
        "function_args":", ".join(inline_string_list),
        "function_inline_variable_declaration":"\n".join(variable_definition_list),
    }


def encode_function_return_type(analyse: AnalyzedFunction):
    # if None is acceptable for return type, set return_none_allowed in meta prompt
    return_type = analyse.type
    if return_type is not None and hasattr(return_type, "__origin__") and return_type.__origin__ is Union:
        args = return_type.__args__
        if type(None) in args:
            return_none_allowed = True
        else:
            return_none_allowed = False
    else:
        return_none_allowed = False    
    return {
        "function_return_type": analyse.type,
        "function_return_type_name": nice_type_name(analyse.type),
        "return_none_allowed": return_none_allowed,
    }
    
def encode_function_return_type_definition(analyse: AnalyzedFunction):

    return {
        "function_return_as_python_type" : describe_type_as_python(analyse.type)
        }
    