from typing import Any, Tuple, Optional, cast
from .primitives import GuardedPrimitive, GuardedCallInput, UncertaintyLevel, Tolerance, ProxyWrapper, CastingResult


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
                    # Convert items if needed
                    converted = [cls._item_type(item) for item in value]
                    # If conversion happened (or types were checked), we return them
                    return UncertaintyLevel(Tolerance.STRICT), converted, None
                except Exception as e:
                    return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
            return UncertaintyLevel(Tolerance.STRICT), value, None
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
                converted = [cls._item_type(item) for item in items]
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
                    converted = {cls._item_type(item) for item in value}
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
                converted = {cls._item_type(item) for item in items}
                return UncertaintyLevel(Tolerance.PRECISE), converted, None
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
                        new_k = cls._key_type(k) if cls._key_type else k
                        new_v = cls._value_type(v) if cls._value_type else v
                        converted[new_k] = new_v
                    return UncertaintyLevel(Tolerance.STRICT), converted, None
                except Exception as e:
                    return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
            return UncertaintyLevel(Tolerance.STRICT), value, None
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
                    new_k = cls._key_type(k) if cls._key_type else k
                    new_v = cls._value_type(v) if cls._value_type else v
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
                    converted = tuple(cls._item_types[i](value[i]) for i in range(len(value)))
                    return UncertaintyLevel(Tolerance.STRICT), converted, None
                except Exception as e:
                    return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
            return UncertaintyLevel(Tolerance.STRICT), value, None
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        items = None
        # Accepter les listes et sets
        if isinstance(value, (list, set, frozenset)):
            items = tuple(value)
        
        # Accepter les strings représentant des tuples
        elif isinstance(value, str):
            value_s = value.strip()
            
            # Format "(1, 2, 3)"
            if value_s.startswith('(') and value_s.endswith(')'):
                try:
                    import ast
                    parsed = ast.literal_eval(value_s)
                    if isinstance(parsed, tuple):
                        items = parsed
                except (ValueError, SyntaxError):
                    pass
            
            # Format "1,2,3" (CSV)
            if items is None and ',' in value_s:
                items = tuple(item.strip() for item in value_s.split(','))
        
        if items is None:
            try:
                items = tuple(value)
            except (TypeError, ValueError):
                return UncertaintyLevel(Tolerance.ANYTHING), value, "Could not convert to tuple"


        # Content validation
        if cls._item_types:
            return cls._content_validation(items, value)
        
        return UncertaintyLevel(Tolerance.PRECISE), items, None

    @classmethod
    def _content_validation(cls, items, value) -> Tuple[UncertaintyLevel, Any, str | None]:
            # Fixed length
        if len(items) != len(cls._item_types):
            return UncertaintyLevel(Tolerance.ANYTHING), value, f"Tuple length mismatch: expected {len(cls._item_types)}, got {len(items)}"
        try:
            converted = tuple(cls._item_types[i](items[i]) for i in range(len(items)))
            return UncertaintyLevel(Tolerance.PRECISE), converted, None
        except Exception as e:
            return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
        

    @classmethod
    def _parse_semantic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, str | None]:
        """
        Try to fix content that makes string not parsable without changing the meaning
        """
        
        if isinstance(value, str):
            value_s = value.strip()
            value_s = value.replace("\n","\\n")
            # Error might me due to newlines in text content
            try:
                import ast
                parsed = ast.literal_eval(value_s)
                if isinstance(parsed, tuple):
                    items = parsed
            except (ValueError, SyntaxError):
                pass

            if cls._item_types:
                return cls._content_validation(items, value)
            
        return UncertaintyLevel(Tolerance.ANYTHING), value, "Could not convert to tuple"

    def unwrap(self):
        """Retourne un tuple natif avec unwrapping récursif des éléments."""
        return self._recursive_unwrap(tuple(self))

def guarded_tuple(*item_types):

    """Factory for parameterized tuples."""
    return GuardedTuple[item_types]

def guarded_dataclass(first_arg=None, **dataclass_kwargs):
    """
    Decorator qui transforme une classe en GuardedDataclass.
    
    Applique automatiquement @dataclass si la classe n'est pas déjà une dataclass.
    
    Usage simple (recommandé) :
        from OpenHosta.guarded import guarded_dataclass
        
        @guarded_dataclass
        class Person:
            name: str
            age: int
        
        p = Person({"name": "Alice", "age": "25"})  # ✅ Accepte dict
        p = Person(name="Bob", age=30)              # ✅ Accepte kwargs
    
    Usage avec options dataclass :
        @guarded_dataclass(frozen=True, order=True)
        class Point:
            x: int
            y: int
    
    Usage avec @dataclass explicite (legacy) :
        from dataclasses import dataclass
        
        @guarded_dataclass
        @dataclass
        class Person:
            name: str
            age: int
    """
    from dataclasses import dataclass, is_dataclass, fields
    from .resolver import TypeResolver

    
    def decorator(cls_to_guard):
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
            _type_py_repr = cls_to_guard.__doc__
            _type_json = {"type": "object"}
            _tolerance = Tolerance.TYPE_COMPLIANT

            @classmethod
            def _coerce_dataclass_inputs(cls, args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
                field_names = [field.name for field in field_definitions]
                merged_kwargs = dict(kwargs)

                if len(args) > len(field_names):
                    raise TypeError(f"Too many positional arguments for {cls_to_guard.__name__}")

                for field_name, arg_value in zip(field_names, args):
                    if field_name in merged_kwargs:
                        raise TypeError(f"Multiple values for field '{field_name}'")
                    merged_kwargs[field_name] = arg_value

                converted_kwargs = {}
                for field in field_definitions:
                    if field.name not in merged_kwargs:
                        continue
                    raw_value = merged_kwargs[field.name]
                    guarded_type = TypeResolver.resolve(field.type)

                    if isinstance(raw_value, guarded_type):
                        converted_value = raw_value
                    else:
                        attempt_result = guarded_type.attempt(raw_value)
                        if not attempt_result.is_success:
                            raise ValueError(attempt_result.error_message)

                        if getattr(guarded_type, "_types", None) is not None:
                            winning_type = attempt_result.python_type
                            converted_value = winning_type(raw_value) if winning_type is not None else attempt_result.python_value
                        elif hasattr(guarded_type, "__dataclass_fields__"):
                            converted_value = guarded_type(raw_value)
                        else:
                            converted_value = attempt_result.python_value



                    converted_kwargs[field.name] = converted_value

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
                if not isinstance(value, str):
                    value = str(value)
                    # We remove comments
                    value = "\n".join([l for l in value.splitlines() if not l.strip().startswith("#")])


                # Si c'est une string qui ressemble à un appel constructeur: Person(...)
                if isinstance(value, str) and (
                    value.strip().startswith(cls.__name__ + "(") or
                    value.strip().startswith("{")
                ):
                    import ast
                    tree = ast.parse(value.strip(), mode='eval')
                    if isinstance(tree.body, ast.Call):
                        parsed_args = []
                        parsed_kwargs = {}
                        for arg in tree.body.args:
                            parsed_args.append(ast.literal_eval(arg))
                        for keyword in tree.body.keywords:
                            parsed_kwargs[keyword.arg] = ast.literal_eval(keyword.value)
                        
                        # Tenter d'instancier avec les args parsés
                        try:
                            # On crée l'instance directement via le constructeur
                            instance = cls._coerce_dataclass_inputs(tuple(parsed_args), parsed_kwargs)
                            return UncertaintyLevel(Tolerance.PRECISE), instance, None

                        except Exception as e:
                            # Si échec instanciation directe, essayer via dict mode si possible ou fail
                            return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)
                    elif isinstance(tree.body, ast.Dict):
                        # Tenter d'instancier avec les args parsés
                        parsed_kwargs = {}
                        for keyword, value in zip(tree.body.keys, tree.body.values):
                            parsed_kwargs[ast.literal_eval(keyword)] = ast.literal_eval(value)
                        try:
                            # On crée l'instance directement via le constructeur
                            instance = cls._coerce_dataclass_inputs((), parsed_kwargs)
                            return UncertaintyLevel(Tolerance.PRECISE), instance, None

                        except Exception as e:
                            # Si échec instanciation directe, essayer via dict mode si possible ou fail
                            return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)

                    else:
                        return UncertaintyLevel(Tolerance.ANYTHING), value, "String format not recognized as constructor call or dict"

                return UncertaintyLevel(Tolerance.ANYTHING), value, f"Could not parse as {cls.__name__} dataclass: id of type {id(type(value))} with value {value}. id of cls {id(cls)}"

            
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
        
        return GuardedDataclassWrapper
    
    # Support pour @guarded_dataclass et @guarded_dataclass()
    if first_arg is None:
        # Appelé avec arguments : @guarded_dataclass() ou @guarded_dataclass(frozen=True)
        return decorator
    else:
        # Appelé sans arguments : @guarded_dataclass, ou aussi en ligne : GuardedType = guarded_dataclass(MyType)
        return decorator(first_arg)


