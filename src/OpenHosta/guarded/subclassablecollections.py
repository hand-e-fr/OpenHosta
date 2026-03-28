from typing import Any, Tuple, Optional
from .primitives import GuardedPrimitive, GuardedCallInput, UncertaintyLevel, Tolerance, ProxyWrapper
from .type_hints import resolve_struct_hints

class GuardedList(GuardedPrimitive, list):
    """
    Liste sémantique.
    Accepte : [1, 2, 3], "[1, 2, 3]", "1,2,3", ou toute itérable.
    """
    _type_en = "a list of items"
    _type_py = list
    _type_json = {"type": "array"}
    _item_type = None


    def __class_getitem__(cls, item):
        class ParameterizedGuardedList(cls):
            _item_type = item
            _type_en = f"a list of {item._type_en if hasattr(item, '_type_en') else str(item)}"
        return ParameterizedGuardedList
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, list):
            if cls._item_type:
                try:
                    converted = []
                    for item in value:
                        r = cls._item_type.attempt(item)
                        # We MUST use r.data to get the native value. 
                        # If attempt fails, it will raise eventually or we fallback to the raw item if we are tolerant.
                        # But for STRICT native parsing, we expect success.
                        if r.success:
                            converted.append(r.data)
                        else:
                            return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {r.error_message}"
                    return UncertaintyLevel(Tolerance.STRICT), converted, None
                except Exception as e:
                    return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
            return UncertaintyLevel(Tolerance.STRICT), list(value), None
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        items = None
        # Accepter les tuples, sets, et autres itérables
        if isinstance(value, (tuple, set, frozenset)):
            items = list(value)
        
        # Accepter les strings représentant des listes
        elif isinstance(value, str):
            value_s = value.strip()
            
            # Format "[1, 2, 3]"
            if value_s.startswith('[') and value_s.endswith(']'):
                try:
                    import ast
                    parsed = ast.literal_eval(value_s)
                    if isinstance(parsed, list):
                        items = parsed
                except (ValueError, SyntaxError) as e:
                    pass
            
            # Format "1,2,3" (CSV)
            if items is None and ',' in value_s:
                items = [item.strip() for item in value_s.split(',')]
        
        # Tenter de convertir en liste
        if items is None:
            try:
                items = list(value)
            except (TypeError, ValueError):
                return UncertaintyLevel(Tolerance.ANYTHING), value, "Could not convert to list"

        # Content validation
        if cls._item_type:
            try:
                converted = []
                for item in items:
                    r = cls._item_type.attempt(item)
                    if r.success:
                        converted.append(r.data)
                    else:
                        return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item validation failed: {r.error_message}"
                return UncertaintyLevel(Tolerance.PRECISE), converted, None
            except Exception as e:
                return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
        
        return UncertaintyLevel(Tolerance.PRECISE), items, None

    def unwrap(self):
        """Retourne une liste native avec unwrapping récursif des éléments."""
        return self._recursive_unwrap(list(self))

class GuardedSet(GuardedPrimitive, set):
    """
    Ensemble sémantique.
    Accepte : {1, 2, 3}, "{1, 2, 3}", "1,2,3", ou toute itérable.
    """
    _type_en = "a set of unique items"
    _type_py = set
    _type_json = {"type": "array", "uniqueItems": True}
    _item_type = None




    def __class_getitem__(cls, item):
        class ParameterizedGuardedSet(cls):
            _item_type = item
            _type_en = f"a set of {item._type_en if hasattr(item, '_type_en') else str(item)}"
        return ParameterizedGuardedSet
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, (set, frozenset)):
            if cls._item_type:
                try:
                    converted = set()
                    for item in value:
                        r = cls._item_type.attempt(item)
                        if r.success:
                            converted.add(r.data)
                        else:
                            return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {r.error_message}"
                    return UncertaintyLevel(Tolerance.STRICT), converted, None
                except Exception as e:
                    return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
            return UncertaintyLevel(Tolerance.STRICT), set(value), None
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        items = None
        # Accepter les listes et tuples
        if isinstance(value, (list, tuple)):
            items = set(value)
        
        # Accepter les strings représentant des sets
        elif isinstance(value, str):
            value_s = value.strip()
            
            # Format "{1, 2, 3}" ou "frozenset({...})" ou "frozenset([...])"
            if value_s.startswith("frozenset(") and value_s.endswith(")"):
                 value_s = value_s[10:-1]
            
            if value_s.startswith('{') and value_s.endswith('}'):
                try:
                    import ast
                    parsed = ast.literal_eval(value_s)
                    if isinstance(parsed, (set, list, tuple)):
                        items = set(parsed)
                except (ValueError, SyntaxError):
                    pass
            elif value_s.startswith('[') and value_s.endswith(']'):
                 # Case frozen_set([1, 2])
                try:
                    import ast
                    parsed = ast.literal_eval(value_s)
                    if isinstance(parsed, list):
                        items = set(parsed)
                except:
                    pass
            
            # Format "1,2,3" (CSV)
            if items is None and ',' in value_s:
                items = {item.strip() for item in value_s.split(',')}
        
        # Tenter de convertir en set
        if items is None:
            try:
                items = set(value)
            except (TypeError, ValueError):
                return UncertaintyLevel(Tolerance.ANYTHING), value, "Could not convert to set"

        # Content validation
        if cls._item_type:
            try:
                converted_items = []
                for item in items:
                    res = cls._item_type.attempt(item)
                    if res.success:
                        converted_items.append(res.data)
                    else:
                        return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item validation failed: {res.error_message}"
                return UncertaintyLevel(Tolerance.PRECISE), set(converted_items), None
            except Exception as e:
                return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
        
        return UncertaintyLevel(Tolerance.PRECISE), items, None

    def unwrap(self):
        """Retourne un set natif avec unwrapping récursif des éléments."""
        return self._recursive_unwrap(set(self))

class GuardedDict(GuardedPrimitive, dict):
    """
    Dictionnaire sémantique.
    Accepte : {"a": 1}, '{"a": 1}', ou tout mapping.
    """
    _type_en = "a dictionary mapping keys to values"
    _type_py = dict
    _type_json = {"type": "object"}
    _key_type = None
    _value_type = None

    def __class_getitem__(cls, item):
        if not isinstance(item, tuple) or len(item) != 2:
            return cls
        class ParameterizedGuardedDict(cls):
            _key_type = item[0]
            _value_type = item[1]
            _type_en = f"a dictionary mapping {item[0]._type_en if hasattr(item[0], '_type_en') else str(item[0])} to {item[1]._type_en if hasattr(item[1], '_type_en') else str(item[1])}"
        return ParameterizedGuardedDict
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, dict):
            if cls._key_type or cls._value_type:
                try:
                    converted = {}
                    for k, v in value.items():
                        if cls._key_type:
                            rk = cls._key_type.attempt(k)
                            if not rk.success:
                                return UncertaintyLevel(Tolerance.ANYTHING), value, f"Key conversion failed: {rk.error_message}"
                            new_k = rk.data
                        else:
                            new_k = k
                            
                        if cls._value_type:
                            rv = cls._value_type.attempt(v)
                            if not rv.success:
                                return UncertaintyLevel(Tolerance.ANYTHING), value, f"Value conversion failed: {rv.error_message}"
                            new_v = rv.data
                        else:
                            new_v = v
                        converted[new_k] = new_v
                    return UncertaintyLevel(Tolerance.STRICT), converted, None
                except Exception as e:
                    return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
            return UncertaintyLevel(Tolerance.STRICT), dict(value), None
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        items = None
        # Accepter les strings représentant des dicts
        if isinstance(value, str):
            value_s = value.strip()
            
            # Format JSON
            if value_s.startswith('{') and value_s.endswith('}'):
                try:
                    import json
                    parsed = json.loads(value_s)
                    if isinstance(parsed, dict):
                        items = parsed
                except (json.JSONDecodeError, ValueError):
                    # Essayer avec ast.literal_eval
                    try:
                        import ast
                        parsed = ast.literal_eval(value_s)
                        if isinstance(parsed, dict):
                            items = parsed
                    except (ValueError, SyntaxError):
                        pass
        
        # Tenter de convertir en dict
        if items is None:
            try:
                items = dict(value)
            except (TypeError, ValueError):
                return UncertaintyLevel(Tolerance.ANYTHING), value, "Could not convert to dict"

        # Content validation
        if cls._key_type or cls._value_type:
            try:
                converted = {}
                for k, v in items.items():
                    if cls._key_type:
                        rk = cls._key_type.attempt(k)
                        if not rk.success:
                            return UncertaintyLevel(Tolerance.ANYTHING), value, f"Key validation failed: {rk.error_message}"
                        new_k = rk.data
                    else:
                        new_k = k
                        
                    if cls._value_type:
                        rv = cls._value_type.attempt(v)
                        if not rv.success:
                            return UncertaintyLevel(Tolerance.ANYTHING), value, f"Value validation failed: {rv.error_message}"
                        new_v = rv.data
                    else:
                        new_v = v
                    converted[new_k] = new_v
                return UncertaintyLevel(Tolerance.PRECISE), converted, None
            except Exception as e:
                return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
        
        return UncertaintyLevel(Tolerance.PRECISE), items, None

    def unwrap(self):
        """Retourne un dict natif avec unwrapping récursif des clés et valeurs."""
        return self._recursive_unwrap(dict(self))

class GuardedTuple(GuardedPrimitive, tuple):

    """
    Tuple sémantique.
    Accepte : (1, 2, 3), "(1, 2, 3)", "1,2,3", ou toute itérable.
    """
    _type_en = "a tuple of items"
    _type_py = tuple
    _type_json = {"type": "array"}
    _item_types = None # None or tuple of types

    def __class_getitem__(cls, items):
        if not isinstance(items, tuple):
            items = (items,)
        
        class ParameterizedGuardedTuple(cls):
            _item_types = items
            _type_en = f"a tuple of ({', '.join(t._type_en if hasattr(t, '_type_en') else str(t) for t in items)})"
        return ParameterizedGuardedTuple
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, tuple):
            if cls._item_types:
                # Variable length if ... (not supported yet) or fixed length
                if len(value) != len(cls._item_types):
                    return UncertaintyLevel(Tolerance.ANYTHING), value, f"Tuple length mismatch: expected {len(cls._item_types)}, got {len(value)}"
                try:
                    converted_items = []
                    for i in range(len(value)):
                        res = cls._item_types[i].attempt(value[i])
                        if res.success:
                            converted_items.append(res.data)
                        else:
                            return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item {i} conversion failed: {res.error_message}"
                    converted = tuple(converted_items)
                    return UncertaintyLevel(Tolerance.STRICT), converted, None
                except Exception as e:
                    return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
            return UncertaintyLevel(Tolerance.STRICT), value, None
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        items = None
        # Accepter les listes et sets
        if isinstance(value, (list, set, frozenset, tuple)):
            items = tuple(value)
        
        # Accepter les strings représentant des tuples
        elif isinstance(value, str):
            value_s = value.strip("\n \t")
            
            # Format "(1, 2, 3)"
            if value_s.startswith('(') and value_s.endswith(')'):
                try:
                    import ast
                    # Attempt to parse using ast.literal_eval for safe evaluation
                    parsed = ast.literal_eval(value_s)
                    if isinstance(parsed, tuple):
                        items = parsed
                    else:
                        return UncertaintyLevel(Tolerance.ANYTHING), value, f"Not a tuple: {value}"
                except (ValueError, SyntaxError):
                    # Handle cases like (<MyEnum.PAS_ASSEZ_INFORMATION: 'pas_assez_information'>, 're')
                    # where ast.literal_eval fails due to non-literal expressions
                    try:
                        # Strip the outer parentheses and split manually by commas not inside nested structures
                        inner = value_s[1:-1].strip()
                        if not inner:
                            items = []
                        else:
                            # Simple split with comma, careful about potential nesting
                            # This is a less safe fallback, but necessary for non-literal enum representations
                            parts = []
                            depth = 0
                            in_quote = False
                            quote_char = None
                            last_idx = 0
                            for i, c in enumerate(inner):
                                if c in '"\'' and (i == 0 or inner[i-1] != '\\'):
                                    if not in_quote:
                                        in_quote = True
                                        quote_char = c
                                    elif quote_char == c:
                                        in_quote = False
                                        quote_char = None
                                
                                if not in_quote:
                                    if c in '({[':
                                        depth += 1
                                    elif c in ')}]':
                                        depth -= 1
                                    elif c == ',' and depth == 0:
                                        parts.append(inner[last_idx:i].strip())
                                        last_idx = i + 1
                            parts.append(inner[last_idx:].strip())

                            # Attempt to evaluate each part individually, fallback to string if needed
                            evaluated_parts = []
                            for part in parts:
                                try:
                                    # First, try literal_eval for safety
                                    evaluated = ast.literal_eval(part)
                                except (ValueError, SyntaxError):
                                    # If that fails, keep it as a string representation
                                    # This preserves things like enum instances that can't be literal-evaluated
                                    evaluated = part
                                evaluated_parts.append(evaluated)

                            items = evaluated_parts
                    except Exception:
                        return UncertaintyLevel(Tolerance.ANYTHING), value, "Could not parse string as tuple"
                except (ValueError, SyntaxError) as e:
                    return UncertaintyLevel(Tolerance.ANYTHING), value, f"Could not parse tuple from string to {cls._type_py}:\n{e}\n{value}"
                    
            # Format "1,2,3" (CSV)
            if items is None and ',' in value_s:
                items = tuple(item.strip() for item in value_s.split(','))
            if items is None:
                items = tuple(value)

        # Content validation
        return cls._content_validation(items, value)
        
    @classmethod
    def _content_validation(cls, items, value) -> Tuple[UncertaintyLevel, Any, str | None]:
            # Fixed length
        if cls._item_types is not None:
            if len(items) != len(cls._item_types):
                return UncertaintyLevel(Tolerance.ANYTHING), value, f"Tuple length mismatch: expected {len(cls._item_types)}, got {len(items)}"
            try:
                converted_items = []
                for i in range(len(items)):
                    item_type = cls._item_types[i]
                    item_result = item_type.attempt(items[i])
                    if item_result.success:
                        converted_items.append(item_result.data)
                    else:
                        return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item {i} validation failed: {item_result.error_message}"
                converted = tuple(converted_items)
                return UncertaintyLevel(Tolerance.PRECISE), converted, None
            except Exception as e:
                return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
        else:
            # inner types for tuple is not defoned. accept anything
            return UncertaintyLevel(Tolerance.PRECISE), items, None

    @classmethod
    def _parse_semantic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, str | None]:
        """
        Try to fix content that makes string not parsable without changing the meaning
        """
        
        if isinstance(value, str):
            value_s = value.strip("\n \t")
            value_s = value.replace("\n","\\n")
            # Error might me due to newlines in text content
            try:
                import ast
                parsed = ast.literal_eval(value_s)
                if isinstance(parsed, tuple):
                    items = parsed
                else:
                    return UncertaintyLevel(Tolerance.ANYTHING), value, f"Not a tuple: {value}"
            except (ValueError, SyntaxError) as e:
                return UncertaintyLevel(Tolerance.ANYTHING), value, f"Could not parse tuple from string to {cls._type_py}:\n{e}\n{value}"

            if cls._item_types:
                return cls._content_validation(items, value)
            else:
                # Si aucun type d'élément n'est spécifié, on accepte le tuple tel quel
                return UncertaintyLevel(Tolerance.STRICT), value, None
                    
        return UncertaintyLevel(Tolerance.ANYTHING), value, "Could not convert to tuple"

    def unwrap(self):
        """Retourne un tuple natif avec unwrapping récursif des éléments."""
        return self._recursive_unwrap(tuple(self))

def guarded_tuple(*item_types):

    """Factory for parameterized tuples."""
    return GuardedTuple[item_types]

# Cache pour éviter de reconstruire la même classe multiple fois
_DATACLASS_GUARDED_CACHE: Any = {}

def guarded_dataclass(first_arg=None, **dataclass_kwargs):
    """
    Decorator qui transforme une classe en GuardedDataclass.
    """
    from dataclasses import dataclass, is_dataclass, fields
    from .resolver import TypeResolver
    
    def decorator(cls_to_guard):
        if cls_to_guard in _DATACLASS_GUARDED_CACHE:
             return _DATACLASS_GUARDED_CACHE[cls_to_guard]
             
        # Si ce n'est pas déjà une dataclass, on l'applique
        if not is_dataclass(cls_to_guard):
            original_type = cls_to_guard
            cls_to_guard = dataclass(cls_to_guard, **dataclass_kwargs)
        else:
            original_type = None

        field_definitions = fields(cls_to_guard)

        class GuardedDataclassWrapper(GuardedPrimitive, ProxyWrapper):


            """Wrapper qui ajoute les capacités Guarded à une dataclass."""
            
            _type_en = f"an instance of {cls_to_guard.__name__} dataclass"
            _type_py = cls_to_guard
            _type_json = {"type": "object"}
            _tolerance = Tolerance.TYPE_COMPLIANT

            @classmethod
            def _coerce_dataclass_inputs(cls, args_tuple, kwargs_dict):
                # Convert args to kwargs based on class fields
                from dataclasses import fields
                field_definitions = fields(cls_to_guard)
                
                merged_kwargs = dict(kwargs_dict)
                hints = resolve_struct_hints(cls_to_guard)
                
                field_names = [field.name for field in field_definitions]
                if len(args_tuple) > len(field_names):
                        raise TypeError(f"Too many positional arguments for {cls_to_guard.__name__}")

                for field_name, arg_value in zip(field_names, args_tuple):
                    if field_name in merged_kwargs:
                        raise TypeError(f"Multiple values for field '{field_name}'")
                    merged_kwargs[field_name] = arg_value

                converted_kwargs = {}
                for field in field_definitions:
                    if field.name not in merged_kwargs:
                        continue
                    raw_value = merged_kwargs[field.name]
                    # Always use hints[field.name] if available to avoid string annotations
                    expected_field_type = hints[field.name] # Changed from hints.get(field.name, field.type)
                    guarded_type = TypeResolver.resolve(expected_field_type)

                    attempt_result = guarded_type.attempt(raw_value)
                    if not attempt_result.success:
                        raise ValueError(attempt_result.error_message)

                    # We use guarded_data for internal storage to preserve metadata and pass core tests
                    converted_kwargs[field.name] = attempt_result.guarded_data

                return cls_to_guard(**converted_kwargs)



            @classmethod
            def _parse_native(cls, value: Any):


                # Tenter d'instancier
                if isinstance(value, cls):
                    return UncertaintyLevel(Tolerance.STRICT), value._python_value, None

                if isinstance(value, cls_to_guard):
                    return UncertaintyLevel(Tolerance.STRICT), value, None


                if isinstance(value, GuardedCallInput):
                    try:
                        native_instance = cls._coerce_dataclass_inputs(value.args, value.kwargs)
                        return UncertaintyLevel(Tolerance.STRICT), native_instance, None
                    except Exception as e:
                        return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)



                if original_type is not None and isinstance(value, original_type):
                    return UncertaintyLevel(Tolerance.STRICT), value, None



                if isinstance(value, dict):
                    try:
                        instance = cls._coerce_dataclass_inputs((), value)
                        return UncertaintyLevel(Tolerance.STRICT), instance, None
                    except Exception as e:
                        return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)

                
                return UncertaintyLevel(Tolerance.ANYTHING), value, f"Could not parse as {cls.__name__} dataclass: id of type {id(type(value))} with value {value}. id of cls {id(cls)}"

            
            @classmethod  
            def _parse_heuristic(cls, value: Any):

                if isinstance(value, GuardedCallInput):
                    try:
                        native_instance = cls._coerce_dataclass_inputs(value.args, value.kwargs)
                        return UncertaintyLevel(Tolerance.PRECISE), native_instance, None
                    except Exception as e:
                        return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)



                # We try to make it as a string if it's not already a string, to let the LLM try to parse it as a constructor call or dict
                v_strip = str(value).strip().replace("\n", "")

                # Obtenir le nom de la classe d'origine (sans le préfixe Guarded_)
                original_name = cls._type_py.__name__ if hasattr(cls, '_type_py') else cls.__name__
                if original_name.startswith("Guarded_") and len(original_name) > 8:
                    original_name = original_name[8:]

                # Si c'est une string qui ressemble à un appel constructeur: Person(...)
                data_dict = None
                if v_strip.startswith(original_name + "(") or v_strip.startswith("{"):
                    import ast
                    try:
                        tree = ast.parse(v_strip, mode='eval')
                        if isinstance(tree.body, ast.Call):
                            parsed_args = [ast.literal_eval(arg) for arg in tree.body.args]
                            parsed_kwargs = {}
                            for kw in tree.body.keywords:
                                try: parsed_kwargs[kw.arg] = ast.literal_eval(kw.value)
                                except: parsed_kwargs[kw.arg] = ast.unparse(kw.value)
                            
                            # Bind signature to get full kwargs dict
                            import inspect
                            sig = inspect.signature(cls_to_guard)
                            bound = sig.bind(*parsed_args, **parsed_kwargs)
                            bound.apply_defaults()
                            data_dict = bound.arguments
                        elif isinstance(tree.body, ast.Dict):
                            try:
                                data_dict = ast.literal_eval(v_strip)
                            except:
                                import json
                                json_v = v_strip.replace('true', 'True').replace('false', 'False').replace('null', 'None')
                                try: data_dict = ast.literal_eval(json_v)
                                except:
                                    try: data_dict = json.loads(v_strip)
                                    except: data_dict = None
                    except Exception:
                        import json
                        try: data_dict = json.loads(v_strip)
                        except: pass

                    try:
                        instance = cls._coerce_dataclass_inputs((), data_dict)
                        # We return the native instance. 
                        # attempt() will wrap it in GuardedDataclassWrapper.
                        # Then pull_type_data_section will unwrap() it if needed.
                        return UncertaintyLevel(Tolerance.PRECISE), instance, None
                    except Exception as e:
                        return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)

                return UncertaintyLevel(Tolerance.ANYTHING), value, f"Could not parse as {cls.__name__} dataclass: {value}"

            
            def unwrap(self):
                return self._recursive_unwrap(self._python_value)

            def __setattr__(self, name, value):
                if name.startswith("_"):
                    object.__setattr__(self, name, value)
                    return

                try:
                    python_value = object.__getattribute__(self, "_python_value")
                except AttributeError:
                    object.__setattr__(self, name, value)
                    return

                if hasattr(type(python_value), "__dataclass_fields__") and name in python_value.__dataclass_fields__:
                    setattr(python_value, name, value)
                    return

                object.__setattr__(self, name, value)




                # Copier les métadonnées de la classe d'origine pour une meilleure introspection et debug        
        GuardedDataclassWrapper.__dataclass_fields__ = getattr(cls_to_guard, "__dataclass_fields__", {})
        GuardedDataclassWrapper.__dataclass_params__ = getattr(cls_to_guard, "__dataclass_params__", None)
        GuardedDataclassWrapper.__match_args__ = getattr(cls_to_guard, "__match_args__", ())
        GuardedDataclassWrapper.__name__ = cls_to_guard.__name__

        GuardedDataclassWrapper.__module__ = cls_to_guard.__module__
        GuardedDataclassWrapper.__qualname__ = cls_to_guard.__qualname__
        GuardedDataclassWrapper.__doc__ = cls_to_guard.__doc__
        # Build Python Representation string to help LLM not hallucinate fields
        fields_repr = []
        hints = resolve_struct_hints(cls_to_guard)

        for field in field_definitions:
            field_type = hints.get(field.name, field.type)
            try:
                guarded_field = TypeResolver.resolve(field_type)
                type_str = getattr(guarded_field, "_type_py_repr", None)
                if type_str is None or type_str is NotImplemented:
                    type_str = getattr(guarded_field, "__name__", str(field_type))
            except Exception:
                type_str = str(field_type)
            fields_repr.append(f"    {field.name}: {type_str}")

        GuardedDataclassWrapper._type_py_repr = (
            f"@dataclass\nclass {cls_to_guard.__name__}:\n" +
            "\n".join(fields_repr)
        )
        
        _DATACLASS_GUARDED_CACHE[cls_to_guard] = GuardedDataclassWrapper
        return GuardedDataclassWrapper
    
    # Support pour @guarded_dataclass et @guarded_dataclass()
    if first_arg is None:
        # Appelé avec arguments : @guarded_dataclass() ou @guarded_dataclass(frozen=True)
        return decorator
    else:
        # Appelé sans arguments : @guarded_dataclass, ou aussi en ligne : GuardedType = guarded_dataclass(MyType)
        return decorator(first_arg)

def guarded_typeddict(cls_to_guard):
    """
    Wrapper for typing.TypedDict.
    Transforms a TypedDict into a GuardedPrimitive.
    """
    from .resolver import TypeResolver

    class GuardedTypedDictWrapper(GuardedPrimitive, ProxyWrapper):
        """Wrapper qui ajoute les capacités Guarded à un TypedDict."""
        
        _type_en = f"a dictionary matching {cls_to_guard.__name__} schema"
        _type_py = dict
        _type_json = {"type": "object"}
        _tolerance = Tolerance.TYPE_COMPLIANT

        @classmethod
        def _coerce_dict(cls, value):
            if not isinstance(value, dict):
                raise ValueError(f"Expected dict, got {type(value)}")
            
            hints = resolve_struct_hints(cls_to_guard)

            converted_dict = {}
            for key, expected_type in hints.items():
                if key in value:
                    guarded_type = TypeResolver.resolve(expected_type)
                    raw_val = value[key]
                    if isinstance(raw_val, guarded_type):
                        converted_dict[key] = raw_val
                    else:
                        attempt_result = guarded_type.attempt(raw_val)
                        if not attempt_result.success:
                            raise ValueError(f"Key '{key}' invalid: {attempt_result.error_message}")
                        
                        _types = getattr(guarded_type, "_types", None)
                        if _types is not None:
                            winning_type = attempt_result.python_type
                            if winning_type is not None:
                                converted_val = winning_type(raw_val)
                            else:
                                converted_val = attempt_result.data
                        elif hasattr(guarded_type, "__dataclass_fields__"):
                            converted_val = guarded_type(raw_val)
                        else:
                            converted_val = attempt_result.data
                            
                        converted_dict[key] = converted_val
                else:
                    required_keys = getattr(cls_to_guard, '__required_keys__', frozenset(hints.keys()))
                    if key in required_keys:
                        raise ValueError(f"Missing required key: '{key}'")

            # Retain any extra keys that might be in the dictionary
            for key, val in value.items():
                if key not in converted_dict:
                    converted_dict[key] = val
                    
            return converted_dict

        @classmethod
        def _parse_native(cls, value: Any):
            if isinstance(value, dict):
                try:
                    converted = cls._coerce_dict(value)
                    return UncertaintyLevel(Tolerance.STRICT), converted, None
                except Exception as e:
                    return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)
            return UncertaintyLevel(Tolerance.ANYTHING), value, f"Not a dict, got {type(value)}"

        @classmethod
        def _parse_heuristic(cls, value: Any):
            import json
            import ast
            items = None
            if isinstance(value, str):
                value_s = value.strip()
                if value_s.startswith('{') and value_s.endswith('}'):
                    try:
                        parsed = json.loads(value_s)
                        if isinstance(parsed, dict):
                            items = parsed
                    except Exception:
                        try:
                            parsed = ast.literal_eval(value_s)
                            if isinstance(parsed, dict):
                                items = parsed
                        except Exception:
                            pass
            if items is None:
                try:
                    items = dict(value)
                except Exception:
                    return UncertaintyLevel(Tolerance.ANYTHING), value, "Could not convert to dict"
            
            try:
                converted = cls._coerce_dict(items)
                return UncertaintyLevel(Tolerance.PRECISE), converted, None
            except Exception as e:
                return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)
                
        def unwrap(self):
            return self._recursive_unwrap(self._python_value)

    GuardedTypedDictWrapper.__name__ = cls_to_guard.__name__
    GuardedTypedDictWrapper.__module__ = getattr(cls_to_guard, '__module__', '')
    GuardedTypedDictWrapper.__qualname__ = getattr(cls_to_guard, '__qualname__', '')
    GuardedTypedDictWrapper.__doc__ = getattr(cls_to_guard, '__doc__', '')

    fields_repr = []
    hints = resolve_struct_hints(cls_to_guard)

    for field_name, field_type in hints.items():
        try:
            guarded_field = TypeResolver.resolve(field_type)
            type_str = getattr(guarded_field, "_type_py_repr", None)
            if type_str is None or type_str is NotImplemented:
                type_str = getattr(field_type, "__name__", str(field_type))
        except Exception:
            type_str = getattr(field_type, "__name__", str(field_type))
        fields_repr.append(f"    {field_name}: {type_str}")

    GuardedTypedDictWrapper._type_py_repr = (
        f"class {cls_to_guard.__name__}(TypedDict):\n" +
        "\n".join(fields_repr)
    )

    return GuardedTypedDictWrapper
