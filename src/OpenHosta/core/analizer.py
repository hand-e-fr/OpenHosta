
import inspect
import typing

from dataclasses import dataclass, field, is_dataclass
from typing import Any, List, Optional, Union

from ..core.base_model import ModelCapabilities
from ..guarded.primitives import GuardedPrimitive
from ..guarded.resolver import TypeResolver
from ..guarded.type_hints import resolve_struct_hints

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
    is_async: bool = False
    is_generator: bool = False
    item_type: Any = str

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
    Returns a Pythonic description of the type.
    """
    if p_type is None or p_type is inspect._empty:
        return ""
    
    try:
        guarded_type = TypeResolver.resolve(p_type)
        type_name = nice_type_name(p_type)
        
        type_py_repr = getattr(guarded_type, "_type_py_repr", NotImplemented)
        if type_py_repr is not NotImplemented:
            type_py_repr_str = str(type_py_repr)
        else:
            type_py_repr_str = str(getattr(guarded_type, "_type_py", ""))
            
        type_en = getattr(guarded_type, "_type_en", "")
        
        doc_lines = []
        doc_lines.append(f"# Type: {type_name}")
        if type_en:
            doc_lines.append(f"# Description: {type_en}")
            
        if "\n" in type_py_repr_str:
            doc_lines.append(type_py_repr_str)
        else:
            doc_lines.append(f"# Python Base: {type_py_repr_str}")
            
        return "\n".join(doc_lines)
    except Exception as e:
        # Fallback if resolution fails
        pass
    
    return f"# {str(p_type)}\n{nice_type_name(p_type)}"

                

def is_typing_type(arg_type):
    # Check if the type provided as argument exist in typing library
    return str(arg_type).startswith("typing.")

def nice_type_name(p_type) -> str:
    """
    Get a nice name for the type to insert in function description for LLM.
    """
    if p_type is None or p_type is inspect._empty:
        return "Any"

    # Handle Python 3.12 TypeAliasType
    if hasattr(p_type, "__name__") and type(p_type).__name__ == "TypeAliasType":
         return p_type.__name__

    # Handle Guarded Types
    # Check if it's a class before issubclass
    if isinstance(p_type, type):
        if issubclass(p_type, GuardedPrimitive):
            # If it's a parameterized guarded type, show it generic-like
            if hasattr(p_type, "_item_type") and p_type._item_type:
                return f"{p_type.__name__}[{nice_type_name(p_type._item_type)}]"
            if hasattr(p_type, "_item_types") and p_type._item_types:
                 return f"{p_type.__name__}[{', '.join(nice_type_name(t) for t in p_type._item_types)}]"
            if hasattr(p_type, "_key_type") and p_type._key_type and hasattr(p_type, "_value_type") and p_type._value_type:
                 return f"{p_type.__name__}[{nice_type_name(p_type._key_type)}, {nice_type_name(p_type._value_type)}]"
            
            # Remove "Guarded_" prefix if present for cleaner look in prompts if it's not a custom name
            name = p_type.__name__
            if name.startswith("Guarded_") and len(name) > 8:
                return name[8:]
            return name

    # Handle typing types and GenericAlias (tuple[int, ...], List[str], etc.)
    if is_typing_type(p_type) or hasattr(p_type, "__origin__"):
        t=repr(p_type)
        # Clean up common prefixes
        t=t.replace("typing.", "")
        t=t.replace("collections.abc.", "")
        t=t.replace("builtins.", "")
        t=t.replace("OpenHosta.guarded.primitives.", "")
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
        doc=analyse.doc,
        is_async=analyse.is_async,
        is_generator=analyse.is_generator,
        item_type=analyse.item_type
    )

def _resolve_annotation(annotation, globalns=None, localns=None):
    """Resolve a potentially-stringified annotation to a real Python type.
    
    When `from __future__ import annotations` is used and `get_type_hints` fails,
    annotations appear as raw strings. This helper tries to eval them in the
    function's namespace to recover the real type.
    
    Returns the resolved type, or `typing.Any` if resolution fails.
    """
    if not isinstance(annotation, str):
        return annotation
    
    import warnings
    try:
        resolved = eval(annotation, globalns or {}, localns or {})
        return resolved
    except Exception:
        warnings.warn(f"[OpenHosta] Could not resolve stringified annotation '{annotation}'. Falling back to Any.")
        return typing.Any



def _unwrap_iterator_type(annotation: Any) -> Any:
    from typing import get_origin, get_args
    import collections.abc
    if annotation is None or annotation is inspect.Parameter.empty:
        return str

    origin = get_origin(annotation)
    args   = get_args(annotation)

    _iter_origins = (
        collections.abc.Iterator,
        collections.abc.Iterable,
        collections.abc.AsyncIterator,
        collections.abc.AsyncIterable,
        collections.abc.Generator,
        collections.abc.AsyncGenerator,
    )

    if origin in _iter_origins:
        if args:
            return args[0]
        return str

    if hasattr(annotation, "__name__") and annotation.__name__ in ("Iterator", "Iterable", "AsyncIterator", "AsyncIterable", "Generator", "AsyncGenerator"):
        if args:
            return args[0]
        return str

    return str

def _is_iterator_type(annotation: Any) -> bool:
    from typing import get_origin
    import collections.abc
    origin = get_origin(annotation)
    _iter_origins = (
        collections.abc.Iterator,
        collections.abc.Iterable,
        collections.abc.AsyncIterator,
        collections.abc.AsyncIterable,
        collections.abc.Generator,
        collections.abc.AsyncGenerator,
    )
    if origin in _iter_origins:
        return True

    if hasattr(annotation, "__name__") and annotation.__name__ in ("Iterator", "Iterable", "AsyncIterator", "AsyncIterable", "Generator", "AsyncGenerator"):
        return True

    return False

def hosta_analyze(frame=None, function_pointer=None) -> AnalyzedFunction:
    try:
        if frame is not None:
            hints = typing.get_type_hints(function_pointer, globalns=frame.f_globals, localns=frame.f_locals)
        else:
            hints = typing.get_type_hints(function_pointer)
    except (NameError, AttributeError):
        # Expected when annotations reference undefined names or missing imports
        hints = {}
    except Exception as e:
        import warnings
        warnings.warn(f"[OpenHosta] Unexpected error resolving type hints for {getattr(function_pointer, '__name__', '?')}: {e}")
        hints = {}

    sig = inspect.signature(function_pointer)
    
    # Determine namespace for resolving stringified annotations
    if frame is not None:
        resolve_globalns = frame.f_globals
        resolve_localns = frame.f_locals
    else:
        resolve_globalns = getattr(function_pointer, '__globals__', {})
        resolve_localns = {}

    result_args_value_table = []
    if frame is not None:
        args_info = inspect.getargvalues(frame)
        for arg in args_info.args:
            arg_type = hints.get(arg, sig.parameters[arg].annotation)
            arg_type = _resolve_annotation(arg_type, resolve_globalns, resolve_localns)
            result_args_value_table.append(AnalyzedArgument(
                name=arg,
                value=args_info.locals[arg],
                type=arg_type
            ))
    else:
        for name, param in sig.parameters.items():
            arg_type = hints.get(name, param.annotation)
            arg_type = _resolve_annotation(arg_type, resolve_globalns, resolve_localns)
            result_args_value_table.append(AnalyzedArgument(
                name=name,
                value=inspect._empty,
                type=arg_type
            ))
    
    result_function_name = function_pointer.__name__
    result_return_type = hints.get('return', sig.return_annotation)
    result_return_type = _resolve_annotation(result_return_type, resolve_globalns, resolve_localns)
    result_docstring = function_pointer.__doc__

    _CO_GENERATOR       = inspect.CO_GENERATOR       # 0x20
    _CO_COROUTINE       = inspect.CO_COROUTINE       # 0x100
    _CO_ASYNC_GENERATOR = inspect.CO_ASYNC_GENERATOR # 0x200

    code_obj = getattr(function_pointer, "__code__", None)
    if code_obj:
        flags = code_obj.co_flags
        is_async = bool(flags & _CO_COROUTINE) or bool(flags & _CO_ASYNC_GENERATOR)
        is_generator = bool(flags & _CO_GENERATOR) or bool(flags & _CO_ASYNC_GENERATOR)
    else:
        is_async = inspect.iscoroutinefunction(function_pointer)
        is_generator = inspect.isgeneratorfunction(function_pointer) or inspect.isasyncgenfunction(function_pointer)

    if not is_generator and _is_iterator_type(result_return_type):
        # The user didn't use 'yield' but the return type is an iterator.
        # We promote the function to a generator mode so emulate() returns a stream.
        is_generator = True

    item_type = _unwrap_iterator_type(result_return_type) if is_generator else result_return_type

    return AnalyzedFunction(
        name=result_function_name,
        args=result_args_value_table,
        type=result_return_type,
        doc=result_docstring,
        is_async=is_async,
        is_generator=is_generator,
        item_type=item_type
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

def _collect_types(p_type, type_list, seen_types=None):
    if seen_types is None:
        seen_types = set()
    
    if p_type is None or p_type is inspect._empty or p_type in seen_types:
        return
    
    seen_types.add(p_type)
    
    is_builtin = False
    
    # 1. Résoudre le type s'il n'est pas déjà un GuardedType
    import typing
    try:
        if getattr(p_type, "__origin__", None) is typing.Literal:
            is_builtin = True
            
        if p_type in TypeResolver._PRIMITIVE_MAP:
            mapped = TypeResolver._PRIMITIVE_MAP[p_type]
            if mapped.__name__ != "GuardedCode":
                is_builtin = True
                
        guarded_type = TypeResolver.resolve(p_type)
    except:
        pass

    # 2. Si c'est un type complexe, on l'ajoute à la liste de documentation
    if not is_builtin:
        type_name = nice_type_name(p_type)
        doc = describe_type_as_python(p_type)
        if doc:
            type_list[type_name] = doc

    # 3. Récursivité
    # Generics
    if hasattr(p_type, "__args__"):
        # Skip Literal values — __args__ for Literal["a", "b"] contains values, not types
        origin = getattr(p_type, "__origin__", None)
        if origin is not typing.Literal:
            for arg in p_type.__args__:
                _collect_types(arg, type_list, seen_types)

    # Champs de Dataclass ou Pydantic
    if is_dataclass(p_type):
        hints = resolve_struct_hints(p_type)
        from dataclasses import fields
        for field in fields(p_type):
            _collect_types(hints.get(field.name, field.type), type_list, seen_types)
    elif hasattr(p_type, "model_fields"): # Pydantic v2
        hints = resolve_struct_hints(p_type)
        for field_name, field_info in p_type.model_fields.items():
            _collect_types(hints.get(field_name, field_info.annotation), type_list, seen_types)

def encode_function_parameter_types(analyse: AnalyzedFunction):
    
    # Types of the arguments when type definition is too long
    # to be included inline in the function call
    python_types_definition_list = {}    
    seen_types = set()

    for a in analyse.args:
        _collect_types(a.type, python_types_definition_list, seen_types)
            
    # Include the return type too
    if analyse.type is not None and analyse.type is not inspect._empty:
        _collect_types(analyse.type, python_types_definition_list, seen_types)
                
    if python_types_definition_list:
        joined_types = "\n\n".join([f"# definition of type {k}:\n{v}" for k, v in python_types_definition_list.items()])
        python_type_definition_dict = joined_types
    else:
        python_type_definition_dict = ""

    return {
        "python_type_definition_dict": python_type_definition_dict
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
        
    return_type_name = nice_type_name(analyse.type)
    
    # If the LLM is expected to return code (GuardedCode/Callable),
    # formatting the signature as `-> str` forces it to generate a string (markdown block)
    # rather than mimicking a python `<function...>` pointer response.
    import typing
    import collections.abc
    from ..guarded.primitives import GuardedPrimitive
    
    is_code = False
    if analyse.type is typing.Callable or analyse.type is collections.abc.Callable:
        is_code = True
    elif getattr(analyse.type, "__origin__", None) in (typing.Callable, collections.abc.Callable):
        is_code = True
    elif isinstance(analyse.type, type) and issubclass(analyse.type, GuardedPrimitive) and analyse.type.__name__ == "GuardedCode":
        is_code = True
        
    if is_code:
        return_type_name = "str"

    return {
        "function_return_type": analyse.type,
        "function_return_type_name": return_type_name,
        "return_none_allowed": return_none_allowed,
    }
    
def encode_function_return_type_definition(analyse: AnalyzedFunction):

    return {
        "function_return_as_python_type" : describe_type_as_python(analyse.type)
        }
    